from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from rest_framework.test import APIClient

from market.models import Asset, AssetPrice
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
    AssetPrice.objects.create(
        asset=self.asset,
        date=date(2025, 1, 2),
        open=Decimal("184.000000"),
        high=Decimal("188.000000"),
        low=Decimal("183.000000"),
        close=Decimal("187.500000"),
        volume=1000,
    )
    AssetPrice.objects.create(
        asset=self.asset,
        date=date(2025, 1, 3),
        open=Decimal("187.000000"),
        high=Decimal("190.000000"),
        low=Decimal("186.000000"),
        close=Decimal("189.250000"),
        volume=1000,
    )
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

  def test_duplicate_portfolio_name_is_case_insensitive(self):
    Portfolio.objects.create(user=self.user, name="Core")

    response = self.client.post(
        "/portfolios",
        {"name": " core ", "cash": "100.00", "base_currency": "USD"},
        format="json",
    )

    self.assertEqual(response.status_code, 400)

  def test_negative_cash_is_rejected(self):
    response = self.client.post(
        "/portfolios",
        {"name": "Risky", "cash": "-1.00", "base_currency": "USD"},
        format="json",
    )

    self.assertEqual(response.status_code, 400)

  def test_unsupported_portfolio_currency_is_rejected(self):
    response = self.client.post(
        "/portfolios",
        {"name": "Global", "cash": "100.00", "base_currency": "EUR"},
        format="json",
    )

    self.assertEqual(response.status_code, 400)
    self.assertIn("base_currency", response.data)

  def test_market_close_holding_uses_price_from_purchase_date(self):
    portfolio = Portfolio.objects.create(user=self.user, name="Core")

    response = self.client.post(
        "/portfolio-holdings",
        {
            "portfolio": portfolio.id,
            "asset": self.asset.id,
            "quantity": "2.00000000",
            "target_weight": "0.2500",
            "purchase_date": "2025-01-03",
            "price_source": PortfolioHolding.PriceSource.MARKET_CLOSE,
        },
        format="json",
    )

    self.assertEqual(response.status_code, 201)
    holding = PortfolioHolding.objects.get(id=response.data["id"])
    self.assertEqual(holding.average_cost, Decimal("189.250000"))
    self.assertEqual(holding.price_date, date(2025, 1, 3))
    self.assertEqual(holding.price_source, PortfolioHolding.PriceSource.MARKET_CLOSE)

  def test_holding_can_be_created_without_manual_target_weight(self):
    portfolio = Portfolio.objects.create(user=self.user, name="Core")

    response = self.client.post(
        "/portfolio-holdings",
        {
            "portfolio": portfolio.id,
            "asset": self.asset.id,
            "quantity": "2.00000000",
            "price_source": PortfolioHolding.PriceSource.MANUAL,
            "average_cost": "123.000000",
        },
        format="json",
    )

    self.assertEqual(response.status_code, 201)
    holding = PortfolioHolding.objects.get(id=response.data["id"])
    self.assertEqual(holding.target_weight, Decimal("0.0000"))

  def test_previous_close_holding_uses_latest_price_before_purchase_date(self):
    portfolio = Portfolio.objects.create(user=self.user, name="Core")

    response = self.client.post(
        "/portfolio-holdings",
        {
            "portfolio": portfolio.id,
            "asset": self.asset.id,
            "quantity": "2.00000000",
            "target_weight": "0.2500",
            "purchase_date": "2025-01-04",
            "price_source": PortfolioHolding.PriceSource.PREVIOUS_CLOSE,
        },
        format="json",
    )

    self.assertEqual(response.status_code, 201)
    holding = PortfolioHolding.objects.get(id=response.data["id"])
    self.assertEqual(holding.average_cost, Decimal("189.250000"))
    self.assertEqual(holding.purchase_date, date(2025, 1, 4))
    self.assertEqual(holding.price_date, date(2025, 1, 3))
    self.assertEqual(holding.price_source, PortfolioHolding.PriceSource.PREVIOUS_CLOSE)

  def test_market_close_rejects_missing_exact_market_date(self):
    portfolio = Portfolio.objects.create(user=self.user, name="Core")

    response = self.client.post(
        "/portfolio-holdings",
        {
            "portfolio": portfolio.id,
            "asset": self.asset.id,
            "quantity": "2.00000000",
            "target_weight": "0.2500",
            "purchase_date": "2025-01-04",
            "price_source": PortfolioHolding.PriceSource.MARKET_CLOSE,
        },
        format="json",
    )

    self.assertEqual(response.status_code, 400)
    self.assertFalse(PortfolioHolding.objects.filter(portfolio=portfolio).exists())

  def test_market_price_mode_rejects_manual_average_cost(self):
    portfolio = Portfolio.objects.create(user=self.user, name="Core")

    response = self.client.post(
        "/portfolio-holdings",
        {
            "portfolio": portfolio.id,
            "asset": self.asset.id,
            "quantity": "2.00000000",
            "target_weight": "0.2500",
            "purchase_date": "2025-01-03",
            "price_source": PortfolioHolding.PriceSource.MARKET_CLOSE,
            "average_cost": "123.000000",
        },
        format="json",
    )

    self.assertEqual(response.status_code, 400)

  def test_manual_price_mode_rejects_purchase_date(self):
    portfolio = Portfolio.objects.create(user=self.user, name="Core")

    response = self.client.post(
        "/portfolio-holdings",
        {
            "portfolio": portfolio.id,
            "asset": self.asset.id,
            "quantity": "2.00000000",
            "target_weight": "0.2500",
            "purchase_date": "2025-01-03",
            "price_source": PortfolioHolding.PriceSource.MANUAL,
            "average_cost": "123.000000",
        },
        format="json",
    )

    self.assertEqual(response.status_code, 400)

  def test_target_weight_cannot_exceed_total_portfolio_allocation(self):
    portfolio = Portfolio.objects.create(user=self.user, name="Core")
    PortfolioHolding.objects.create(
        portfolio=portfolio,
        asset=self.asset,
        target_weight=Decimal("0.8000"),
    )
    msft = Asset.objects.get(symbol="MSFT")

    response = self.client.post(
        "/portfolio-holdings",
        {
            "portfolio": portfolio.id,
            "asset": msft.id,
            "quantity": "1.00000000",
            "target_weight": "0.2500",
            "price_source": PortfolioHolding.PriceSource.MANUAL,
            "average_cost": "250.000000",
        },
        format="json",
    )

    self.assertEqual(response.status_code, 400)

  def test_resolve_price_endpoint_returns_previous_close_preview(self):
    response = self.client.get(
        f"/portfolio-holdings/resolve-price?asset={self.asset.id}"
        "&purchase_date=2025-01-04&price_source=previous_close"
    )

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.data["average_cost"], "189.250000")
    self.assertEqual(response.data["price_date"], date(2025, 1, 3))
    self.assertEqual(response.data["price_source"], PortfolioHolding.PriceSource.PREVIOUS_CLOSE)
