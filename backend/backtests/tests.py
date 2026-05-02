from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from market.models import Asset
from strategies.models import Strategy

User = get_user_model()


class BacktestApiTests(TestCase):
  def test_backtest_requires_own_or_public_strategy(self):
    owner = User.objects.create_user(username="owner", email="owner@example.com", password="password123")
    other = User.objects.create_user(username="other", email="other@example.com", password="password123")
    stock = Asset.objects.get(symbol="AAPL")
    private_strategy = Strategy.objects.create(owner=other, name="Private", config={}, is_public=False)
    public_strategy = Strategy.objects.create(owner=other, name="Public", config={}, is_public=True)

    client = APIClient()
    client.force_authenticate(owner)
    payload = {
        "strategy": private_strategy.id,
        "stock": stock.id,
        "start_date": "2025-01-02",
        "end_date": "2025-01-02",
        "initial_cash": "10000.00",
    }

    private_response = client.post("/backtests", payload, format="json")
    public_response = client.post(
        "/backtests",
        {**payload, "strategy": public_strategy.id},
        format="json",
    )

    self.assertEqual(private_response.status_code, 400)
    self.assertEqual(public_response.status_code, 201)
