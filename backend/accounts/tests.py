from django.contrib.auth import get_user_model
from django.test import TestCase
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
