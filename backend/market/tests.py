from decimal import Decimal

from django.db import connection
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient

from market.models import Asset, AssetPrice


class MarketModelTests(TestCase):
  def test_asset_price_unique_per_asset_and_date(self):
    asset = Asset.objects.get(symbol="AAPL")
    price_data = {
        "asset": asset,
        "date": "2025-01-02",
        "open": Decimal("185.0"),
        "high": Decimal("187.5"),
        "low": Decimal("183.4"),
        "close": Decimal("186.2"),
        "volume": 51234567,
    }

    AssetPrice.objects.create(**price_data)

    with self.assertRaises(IntegrityError), transaction.atomic():
      AssetPrice.objects.create(**price_data)

    asset.refresh_from_db()
    self.assertEqual(asset.symbol, "AAPL")

  def test_assets_api_lists_seeded_assets(self):
    asset = Asset.objects.get(symbol="AAPL")
    AssetPrice.objects.create(
        asset=asset,
        date="2025-01-02",
        open=Decimal("185.0"),
        high=Decimal("187.5"),
        low=Decimal("183.4"),
        close=Decimal("186.2"),
        adjusted_close=Decimal("186.2"),
        volume=51234567,
        source="test",
    )

    response = APIClient().get("/api/assets")

    self.assertEqual(response.status_code, 200)
    symbols = {asset["symbol"] for asset in response.data}
    self.assertIn("AAPL", symbols)
    self.assertIn("SPY", symbols)
    self.assertIn("GC=F", symbols)
    aapl = next(asset for asset in response.data if asset["symbol"] == "AAPL")
    self.assertEqual(aapl["latest_price"]["close"], "186.200000")

  def test_assets_api_uses_bounded_queries_for_latest_prices(self):
    asset = Asset.objects.get(symbol="AAPL")
    AssetPrice.objects.create(
        asset=asset,
        date="2025-01-02",
        open=Decimal("185.0"),
        high=Decimal("187.5"),
        low=Decimal("183.4"),
        close=Decimal("186.2"),
        adjusted_close=Decimal("186.2"),
        volume=51234567,
        source="test",
    )

    with CaptureQueriesContext(connection) as queries:
      response = APIClient().get("/api/assets")

    self.assertEqual(response.status_code, 200)
    self.assertLessEqual(len(queries), 2)

  def test_asset_prices_api_filters_by_date_range(self):
    asset = Asset.objects.get(symbol="AAPL")
    AssetPrice.objects.create(
        asset=asset,
        date="2025-01-02",
        open=Decimal("185.0"),
        high=Decimal("187.5"),
        low=Decimal("183.4"),
        close=Decimal("186.2"),
        adjusted_close=Decimal("186.2"),
        volume=51234567,
        source="test",
    )

    response = APIClient().get("/api/assets/AAPL/prices?start=2025-01-01&end=2025-01-31")

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.data["asset"]["symbol"], "AAPL")
    self.assertEqual(len(response.data["prices"]), 1)
    self.assertEqual(response.data["prices"][0]["source"], "test")

  def test_asset_prices_api_rejects_invalid_symbol(self):
    response = APIClient().get("/api/assets/AAPL%27%20OR%201=1/prices")

    self.assertEqual(response.status_code, 400)

  def test_asset_prices_api_rejects_large_date_range(self):
    allowed_response = APIClient().get("/api/assets/AAPL/prices?start=2021-01-01&end=2025-12-31")
    response = APIClient().get("/api/assets/AAPL/prices?start=2020-01-01&end=2026-01-01")

    self.assertEqual(allowed_response.status_code, 200)
    self.assertEqual(response.status_code, 400)
    self.assertIn("Date range cannot exceed", response.data["detail"])
