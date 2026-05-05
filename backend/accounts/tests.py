from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

User = get_user_model()


class AuthApiTests(TestCase):
  def setUp(self):
    self.client = APIClient()

  def test_register_and_login_with_email_or_username(self):
    register_response = self.client.post(
        "/auth/register",
        {
            "username": "alice",
            "email": "Alice@example.com",
            "password": "password123",
            "full_name": "Alice",
        },
        format="json",
    )

    self.assertEqual(register_response.status_code, 201)
    self.assertIn("access_token", register_response.data)
    self.assertEqual(register_response.data["user"]["email"], "alice@example.com")

    email_login_response = self.client.post(
        "/auth/login",
        {"identifier": "alice@example.com", "password": "password123"},
        format="json",
    )
    username_login_response = self.client.post(
        "/auth/login",
        {"identifier": "alice", "password": "password123"},
        format="json",
    )

    self.assertEqual(email_login_response.status_code, 200)
    self.assertEqual(username_login_response.status_code, 200)

  def test_disabled_user_cannot_login(self):
    user = User.objects.create_user(
        username="disabled",
        email="disabled@example.com",
        password="password123",
        is_active=False,
    )

    response = self.client.post(
        "/auth/login",
        {"identifier": user.email, "password": "password123"},
        format="json",
    )

    self.assertEqual(response.status_code, 403)

  def test_duplicate_email_and_username_are_rejected_case_insensitive(self):
    User.objects.create_user(username="alice", email="alice@example.com", password="password123")

    response = self.client.post(
        "/auth/register",
        {
            "username": "ALICE",
            "email": "ALICE@example.com",
            "password": "password123",
        },
        format="json",
    )

    self.assertEqual(response.status_code, 400)

  def test_register_rejects_sql_like_username(self):
    response = self.client.post(
        "/auth/register",
        {
            "username": "alice' OR 1=1--",
            "email": "alice@example.com",
            "password": "password123",
        },
        format="json",
    )

    self.assertEqual(response.status_code, 400)
    self.assertFalse(User.objects.filter(email="alice@example.com").exists())

  def test_login_sql_like_identifier_does_not_authenticate(self):
    User.objects.create_user(username="alice", email="alice@example.com", password="password123")

    response = self.client.post(
        "/auth/login",
        {"identifier": "' OR 1=1 --", "password": "password123"},
        format="json",
    )

    self.assertEqual(response.status_code, 401)
    self.assertNotIn("access_token", response.data)

  def test_profile_update_rejects_sql_like_username(self):
    user = User.objects.create_user(username="alice", email="alice@example.com", password="password123")
    self.client.force_authenticate(user=user)

    response = self.client.patch(
        "/users/me",
        {"username": "bob'; DROP TABLE accounts_user;--"},
        format="json",
    )

    self.assertEqual(response.status_code, 400)
    user.refresh_from_db()
    self.assertEqual(user.username, "alice")

  def test_password_change_sql_like_current_password_does_not_bypass_check(self):
    user = User.objects.create_user(username="alice", email="alice@example.com", password="password123")
    self.client.force_authenticate(user=user)

    response = self.client.patch(
        "/users/me/password",
        {
            "current_password": "' OR 1=1 --",
            "new_password": "newpassword123",
        },
        format="json",
    )

    self.assertEqual(response.status_code, 400)
    user.refresh_from_db()
    self.assertTrue(user.check_password("password123"))
    self.assertFalse(user.check_password("newpassword123"))

  def test_social_login_rejects_unknown_provider(self):
    response = self.client.post("/auth/social/unknown/start", {}, format="json")

    self.assertEqual(response.status_code, 404)

  @override_settings(GOOGLE_OAUTH_CLIENT_ID="", GOOGLE_OAUTH_CLIENT_SECRET="")
  def test_social_login_requires_provider_configuration(self):
    response = self.client.post("/auth/social/google/start", {}, format="json")

    self.assertEqual(response.status_code, 503)

  @override_settings(
      GOOGLE_OAUTH_CLIENT_ID="google-client-id",
      GOOGLE_OAUTH_CLIENT_SECRET="google-client-secret",
      GOOGLE_OAUTH_REDIRECT_URI="http://localhost:3000/auth/callback/google",
  )
  def test_social_login_start_returns_authorization_url(self):
    response = self.client.post("/auth/social/google/start", {}, format="json")

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.data["provider"], "google")
    self.assertIn("state", response.data)
    self.assertIn("https://accounts.google.com/o/oauth2/v2/auth", response.data["authorization_url"])


class PrivateRouteAuthTests(TestCase):
  def setUp(self):
    self.client = APIClient()

  def test_private_routes_reject_anonymous_users(self):
    routes = (
        ("GET", "/auth/me"),
        ("GET", "/users/me"),
        ("PATCH", "/users/me"),
        ("PATCH", "/users/me/password"),
        ("GET", "/users"),
        ("GET", "/strategies"),
        ("GET", "/backtests"),
        ("GET", "/chats"),
        ("GET", "/chat-messages"),
        ("GET", "/debates"),
        ("GET", "/debate-messages"),
    )

    for method, route in routes:
      with self.subTest(route=route):
        response = getattr(self.client, method.lower())(route, {}, format="json")
        self.assertEqual(response.status_code, 401)
