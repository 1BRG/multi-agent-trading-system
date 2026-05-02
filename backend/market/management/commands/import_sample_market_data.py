import csv
from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand

from market.models import Asset, AssetPrice


class Command(BaseCommand):
  help = "Import sample assets and historical prices from the data directory."

  def handle(self, *args, **options):
    data_dir = settings.BASE_DIR.parent / "data"
    stocks_path = data_dir / "sample_stocks.csv"
    prices_path = data_dir / "sample_prices.csv"

    with stocks_path.open(newline="", encoding="utf-8") as stocks_file:
      for row in csv.DictReader(stocks_file):
        Asset.objects.update_or_create(
            symbol=row["symbol"],
            defaults={
                "name": row["name"],
                "asset_type": row.get("asset_type") or Asset.AssetType.STOCK,
                "sector": row.get("sector", ""),
            },
        )

    with prices_path.open(newline="", encoding="utf-8") as prices_file:
      for row in csv.DictReader(prices_file):
        asset = Asset.objects.get(symbol=row["symbol"].upper())
        close = Decimal(row["close"])
        AssetPrice.objects.update_or_create(
            asset=asset,
            date=row["date"],
            defaults={
                "open": Decimal(row["open"]),
                "high": Decimal(row["high"]),
                "low": Decimal(row["low"]),
                "close": close,
                "adjusted_close": Decimal(row.get("adjusted_close") or close),
                "volume": int(row["volume"]),
                "source": row.get("source") or "sample_csv",
            },
        )

    self.stdout.write(self.style.SUCCESS("Sample market data imported."))
