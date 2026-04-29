from decimal import Decimal

from django.db import IntegrityError, transaction
from django.test import TestCase

from market.models import Stock, StockPrice


class MarketModelTests(TestCase):
  def test_stock_price_unique_per_stock_and_date(self):
    stock = Stock.objects.create(symbol="aapl", name="Apple Inc.")
    price_data = {
        "stock": stock,
        "date": "2025-01-02",
        "open": Decimal("185.0"),
        "high": Decimal("187.5"),
        "low": Decimal("183.4"),
        "close": Decimal("186.2"),
        "volume": 51234567,
    }

    StockPrice.objects.create(**price_data)

    with self.assertRaises(IntegrityError), transaction.atomic():
      StockPrice.objects.create(**price_data)

    stock.refresh_from_db()
    self.assertEqual(stock.symbol, "AAPL")
