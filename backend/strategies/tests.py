from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from strategies.models import Strategy

User = get_user_model()


class StrategyApiTests(TestCase):
  def test_user_sees_own_and_public_strategies_only(self):
    owner = User.objects.create_user(username="owner", email="owner@example.com", password="password123")
    other = User.objects.create_user(username="other", email="other@example.com", password="password123")
    Strategy.objects.create(owner=owner, name="Private", config={}, is_public=False)
    Strategy.objects.create(owner=other, name="Public", config={}, is_public=True)
    Strategy.objects.create(owner=other, name="Other private", config={}, is_public=False)

    client = APIClient()
    client.force_authenticate(owner)
    response = client.get("/strategies")

    self.assertEqual(response.status_code, 200)
    self.assertEqual({item["name"] for item in response.data}, {"Private", "Public"})
