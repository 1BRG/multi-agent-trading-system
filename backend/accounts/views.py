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

    if not user.is_active:
      return Response({"detail": "User account is disabled."}, status=status.HTTP_403_FORBIDDEN)

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
