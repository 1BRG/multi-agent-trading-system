import re
import secrets
from urllib.parse import urlencode

import httpx
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.serializers import (
    LoginSerializer,
    PasswordChangeSerializer,
    RegisterSerializer,
    UserProfileUpdateSerializer,
    UserSerializer,
    find_user_by_identifier,
)

User = get_user_model()


SOCIAL_AUTH_PROVIDERS = {
    "google": {
        "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "userinfo_url": "https://openidconnect.googleapis.com/v1/userinfo",
        "scope": "openid email profile",
        "client_id_env": "GOOGLE_OAUTH_CLIENT_ID",
        "client_secret_env": "GOOGLE_OAUTH_CLIENT_SECRET",
        "redirect_uri_env": "GOOGLE_OAUTH_REDIRECT_URI",
    },
    "github": {
        "authorize_url": "https://github.com/login/oauth/authorize",
        "token_url": "https://github.com/login/oauth/access_token",
        "userinfo_url": "https://api.github.com/user",
        "emails_url": "https://api.github.com/user/emails",
        "scope": "read:user user:email",
        "client_id_env": "GITHUB_OAUTH_CLIENT_ID",
        "client_secret_env": "GITHUB_OAUTH_CLIENT_SECRET",
        "redirect_uri_env": "GITHUB_OAUTH_REDIRECT_URI",
    },
}


def auth_response_for_user(user: User, status_code: int = status.HTTP_200_OK) -> Response:
  refresh = RefreshToken.for_user(user)
  return Response(
      {
          "access_token": str(refresh.access_token),
          "refresh_token": str(refresh),
          "token_type": "bearer",
          "user": UserSerializer(user).data,
      },
      status=status_code,
  )


def get_social_provider_config(provider: str) -> dict | None:
  provider_config = SOCIAL_AUTH_PROVIDERS.get(provider)
  if not provider_config:
    return None

  client_id = getattr(settings, provider_config["client_id_env"], "")
  client_secret = getattr(settings, provider_config["client_secret_env"], "")
  redirect_uri = getattr(settings, provider_config["redirect_uri_env"], "")
  if not redirect_uri:
    redirect_uri = f"{settings.FRONTEND_ORIGIN}/auth/callback/{provider}"

  return {
      **provider_config,
      "client_id": client_id,
      "client_secret": client_secret,
      "redirect_uri": redirect_uri,
  }


def social_provider_not_configured(provider: str) -> Response:
  return Response(
      {
          "detail": (
              f"{provider.title()} login is not configured. "
              "Set the OAuth client id and secret in the backend environment."
          )
      },
      status=status.HTTP_503_SERVICE_UNAVAILABLE,
  )


def generate_unique_username(email: str) -> str:
  base_username = re.sub(r"[^a-zA-Z0-9_]+", "_", email.split("@", 1)[0]).strip("_")
  base_username = base_username[:140] or "user"
  username = base_username
  suffix = 1

  while User.objects.filter(username__iexact=username).exists():
    suffix_text = f"_{suffix}"
    username = f"{base_username[:150 - len(suffix_text)]}{suffix_text}"
    suffix += 1

  return username


def get_or_create_social_user(email: str, full_name: str = "") -> User:
  normalized_email = email.strip().lower()
  user = User.objects.filter(email__iexact=normalized_email).first()
  if user:
    return user

  return User.objects.create_user(
      username=generate_unique_username(normalized_email),
      email=normalized_email,
      full_name=full_name.strip(),
  )


def require_active_user(user: User) -> Response | None:
  if not user.is_active:
    return Response({"detail": "User account is disabled."}, status=status.HTTP_403_FORBIDDEN)
  return None


def exchange_social_code_for_profile(provider: str, provider_config: dict, code: str) -> dict[str, str]:
  token_payload = {
      "client_id": provider_config["client_id"],
      "client_secret": provider_config["client_secret"],
      "code": code,
      "redirect_uri": provider_config["redirect_uri"],
  }
  if provider == "google":
    token_payload["grant_type"] = "authorization_code"

  with httpx.Client(timeout=10.0) as client:
    token_response = client.post(
        provider_config["token_url"],
        data=token_payload,
        headers={"Accept": "application/json"},
    )
    token_response.raise_for_status()
    token_data = token_response.json()
    access_token = token_data.get("access_token")
    if not access_token:
      raise ValueError("Social login provider did not return an access token.")

    if provider == "google":
      return get_google_profile(client, provider_config, access_token)

    if provider == "github":
      return get_github_profile(client, provider_config, access_token)

  raise ValueError("Unsupported social login provider.")


def get_google_profile(client: httpx.Client, provider_config: dict, access_token: str) -> dict[str, str]:
  profile_response = client.get(
      provider_config["userinfo_url"],
      headers={"Authorization": f"Bearer {access_token}"},
  )
  profile_response.raise_for_status()
  profile_data = profile_response.json()

  if not profile_data.get("email_verified"):
    raise ValueError("Google account email is not verified.")

  email = profile_data.get("email")
  if not email:
    raise ValueError("Google account did not provide an email address.")

  return {
      "email": email,
      "full_name": profile_data.get("name", ""),
  }


def get_github_profile(client: httpx.Client, provider_config: dict, access_token: str) -> dict[str, str]:
  headers = {
      "Accept": "application/vnd.github+json",
      "Authorization": f"Bearer {access_token}",
  }
  profile_response = client.get(provider_config["userinfo_url"], headers=headers)
  profile_response.raise_for_status()
  profile_data = profile_response.json()

  email = profile_data.get("email")
  if not email:
    emails_response = client.get(provider_config["emails_url"], headers=headers)
    emails_response.raise_for_status()
    emails_data = emails_response.json()
    primary_email = next(
        (
            item.get("email")
            for item in emails_data
            if item.get("primary") and item.get("verified") and item.get("email")
        ),
        None,
    )
    email = primary_email

  if not email:
    raise ValueError("GitHub account did not provide a verified email address.")

  return {
      "email": email,
      "full_name": profile_data.get("name") or profile_data.get("login") or "",
  }


class RegisterView(APIView):
  permission_classes = [permissions.AllowAny]

  def post(self, request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    return auth_response_for_user(user, status.HTTP_201_CREATED)


class LoginView(APIView):
  permission_classes = [permissions.AllowAny]

  def post(self, request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = find_user_by_identifier(serializer.validated_data["identifier"])
    if user is None or not user.check_password(serializer.validated_data["password"]):
      return Response({"detail": "Invalid username/email or password."}, status=status.HTTP_401_UNAUTHORIZED)

    inactive_response = require_active_user(user)
    if inactive_response:
      return inactive_response

    return auth_response_for_user(user)


class SocialAuthStartView(APIView):
  permission_classes = [permissions.AllowAny]

  def post(self, request, provider):
    provider = provider.lower()
    provider_config = get_social_provider_config(provider)
    if provider_config is None:
      return Response({"detail": "Unsupported social login provider."}, status=status.HTTP_404_NOT_FOUND)

    if not provider_config["client_id"] or not provider_config["client_secret"]:
      return social_provider_not_configured(provider)

    state = secrets.token_urlsafe(32)
    params = {
        "client_id": provider_config["client_id"],
        "redirect_uri": provider_config["redirect_uri"],
        "response_type": "code",
        "scope": provider_config["scope"],
        "state": state,
    }
    if provider == "google":
      params["access_type"] = "offline"
      params["prompt"] = "select_account"

    return Response(
        {
            "authorization_url": f"{provider_config['authorize_url']}?{urlencode(params)}",
            "provider": provider,
            "state": state,
        }
    )


class SocialAuthCallbackView(APIView):
  permission_classes = [permissions.AllowAny]

  def post(self, request, provider):
    provider = provider.lower()
    provider_config = get_social_provider_config(provider)
    if provider_config is None:
      return Response({"detail": "Unsupported social login provider."}, status=status.HTTP_404_NOT_FOUND)

    if not provider_config["client_id"] or not provider_config["client_secret"]:
      return social_provider_not_configured(provider)

    code = request.data.get("code")
    if not code:
      return Response({"code": "This field is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
      profile = exchange_social_code_for_profile(provider, provider_config, code)
    except httpx.HTTPError:
      return Response(
          {"detail": "Could not complete social login with the selected provider."},
          status=status.HTTP_502_BAD_GATEWAY,
      )
    except ValueError as error:
      return Response({"detail": str(error)}, status=status.HTTP_400_BAD_REQUEST)

    user = get_or_create_social_user(profile["email"], profile.get("full_name", ""))
    inactive_response = require_active_user(user)
    if inactive_response:
      return inactive_response

    return auth_response_for_user(user)


class CurrentUserView(APIView):
  def get(self, request):
    return Response(UserSerializer(request.user).data)


class UserMeView(APIView):
  def get(self, request):
    return Response(UserSerializer(request.user).data)

  def patch(self, request):
    serializer = UserProfileUpdateSerializer(request.user, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(UserSerializer(request.user).data)

  def delete(self, request):
    request.user.is_active = False
    request.user.save(update_fields=["is_active", "updated_at"])
    return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordChangeView(APIView):
  def patch(self, request):
    serializer = PasswordChangeSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    request.user.set_password(serializer.validated_data["new_password"])
    request.user.save(update_fields=["password", "updated_at"])
    return Response(status=status.HTTP_204_NO_CONTENT)


class IsAdminRole(permissions.BasePermission):
  def has_permission(self, request, view):
    return bool(
        request.user
        and request.user.is_authenticated
        and (request.user.role == User.Role.ADMIN or request.user.is_staff)
    )


class UserAdminViewSet(viewsets.ModelViewSet):
  serializer_class = UserSerializer
  permission_classes = [IsAdminRole]
  queryset = User.objects.order_by("id")

  def destroy(self, request, *args, **kwargs):
    user = self.get_object()
    user.is_active = False
    user.save(update_fields=["is_active", "updated_at"])
    return Response(status=status.HTTP_204_NO_CONTENT)
