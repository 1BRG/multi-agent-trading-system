import csv
from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand

from market.models import Stock, StockPrice


class Command(BaseCommand):
  help = "Import sample stocks and historical prices from the data directory."

  def handle(self, *args, **options):
    data_dir = settings.BASE_DIR.parent / "data"
    stocks_path = data_dir / "sample_stocks.csv"
    prices_path = data_dir / "sample_prices.csv"

    with stocks_path.open(newline="", encoding="utf-8") as stocks_file:
      for row in csv.DictReader(stocks_file):
        Stock.objects.update_or_create(
            symbol=row["symbol"],
            defaults={
                "name": row["name"],
                "sector": row.get("sector", ""),
            },
        )

    with prices_path.open(newline="", encoding="utf-8") as prices_file:
      for row in csv.DictReader(prices_file):
        stock = Stock.objects.get(symbol=row["symbol"].upper())
        close = Decimal(row["close"])
        StockPrice.objects.update_or_create(
            stock=stock,
            date=row["date"],
            defaults={
                "open": Decimal(row["open"]),
                "high": Decimal(row["high"]),
                "low": Decimal(row["low"]),
                "close": close,
                "adjusted_close": Decimal(row.get("adjusted_close") or close),
                "volume": int(row["volume"]),
            },
        )

    self.stdout.write(self.style.SUCCESS("Sample market data imported."))
