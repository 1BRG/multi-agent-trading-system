from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from rest_framework.test import APIClient

from market.models import Asset
from portfolios.models import Portfolio, PortfolioHolding

User = get_user_model()


class PortfolioApiTests(TestCase):
  def setUp(self):
    self.client = APIClient()
    self.user = User.objects.create_user(
        username="alice",
        email="alice@example.com",
        password="password123",
    )
    self.other_user = User.objects.create_user(
        username="bob",
        email="bob@example.com",
        password="password123",
    )
    self.asset = Asset.objects.get(symbol="AAPL")
    self.client.force_authenticate(self.user)

  def test_user_only_sees_own_portfolios(self):
    own_portfolio = Portfolio.objects.create(user=self.user, name="Long Term")
    Portfolio.objects.create(user=self.other_user, name="Other Portfolio")

    response = self.client.get("/portfolios")

    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(response.data), 1)
    self.assertEqual(response.data[0]["id"], own_portfolio.id)

  def test_create_portfolio_assigns_current_user(self):
    response = self.client.post(
        "/portfolios",
        {
            "name": "Core Portfolio",
            "cash": "2500.00",
            "base_currency": "usd",
            "description": "Main holdings",
        },
        format="json",
    )

    self.assertEqual(response.status_code, 201)
    portfolio = Portfolio.objects.get(id=response.data["id"])
    self.assertEqual(portfolio.user, self.user)
    self.assertEqual(portfolio.base_currency, "USD")

  def test_cannot_add_holding_to_another_users_portfolio(self):
    other_portfolio = Portfolio.objects.create(user=self.other_user, name="Other")

    response = self.client.post(
        "/portfolio-holdings",
        {
            "portfolio": other_portfolio.id,
            "asset": self.asset.id,
            "target_weight": "0.2500",
            "quantity": "1.00000000",
        },
        format="json",
    )

    self.assertEqual(response.status_code, 400)
    self.assertFalse(PortfolioHolding.objects.exists())

  def test_cannot_read_another_users_portfolio(self):
    other_portfolio = Portfolio.objects.create(user=self.other_user, name="Other")

    response = self.client.get(f"/portfolios/{other_portfolio.id}")

    self.assertEqual(response.status_code, 404)

  def test_portfolio_response_includes_holdings(self):
    portfolio = Portfolio.objects.create(user=self.user, name="Core")
    PortfolioHolding.objects.create(
        portfolio=portfolio,
        asset=self.asset,
        target_weight=Decimal("0.5000"),
        quantity=Decimal("2.00000000"),
        average_cost=Decimal("185.000000"),
    )

    response = self.client.get(f"/portfolios/{portfolio.id}")

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.data["holdings"][0]["asset_symbol"], "AAPL")
    self.assertEqual(response.data["holdings"][0]["target_weight"], "0.5000")

  def test_duplicate_asset_in_same_portfolio_is_rejected(self):
    portfolio = Portfolio.objects.create(user=self.user, name="Core")
    PortfolioHolding.objects.create(portfolio=portfolio, asset=self.asset, target_weight=Decimal("0.5000"))

    with self.assertRaises(IntegrityError), transaction.atomic():
      PortfolioHolding.objects.create(portfolio=portfolio, asset=self.asset, target_weight=Decimal("0.2500"))

  def test_duplicate_holding_api_returns_validation_error(self):
    portfolio = Portfolio.objects.create(user=self.user, name="Core")
    PortfolioHolding.objects.create(portfolio=portfolio, asset=self.asset, target_weight=Decimal("0.5000"))

    response = self.client.post(
        "/portfolio-holdings",
        {
            "portfolio": portfolio.id,
            "asset": self.asset.id,
            "target_weight": "0.2500",
        },
        format="json",
    )

    self.assertEqual(response.status_code, 400)
    self.assertEqual(PortfolioHolding.objects.count(), 1)
