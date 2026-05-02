from datetime import date

from django.core.management.base import BaseCommand, CommandError
from django.utils.dateparse import parse_date

from market.data_importer import DEFAULT_HISTORY_START_DATE, import_historical_prices, seed_supported_assets


class Command(BaseCommand):
  help = "Download and import daily OHLCV data for supported assets into PostgreSQL."

  def add_arguments(self, parser):
    parser.add_argument("--symbol", action="append", dest="symbols", help="Import only this symbol. Can be repeated.")
    parser.add_argument("--start", default=DEFAULT_HISTORY_START_DATE.isoformat(), help="Start date in YYYY-MM-DD format.")
    parser.add_argument("--end", default=None, help="End date in YYYY-MM-DD format. Defaults to today.")

  def handle(self, *args, **options):
    start_date = parse_required_date(options["start"], "start")
    end_date = parse_optional_date(options["end"], "end")
    assets = seed_supported_assets(options.get("symbols"))

    if not assets:
      raise CommandError("No supported assets matched the requested symbols.")

    total_rows = 0
    for asset in assets:
      imported_count = import_historical_prices(asset=asset, start_date=start_date, end_date=end_date)
      total_rows += imported_count
      self.stdout.write(f"{asset.symbol}: imported/updated {imported_count} rows.")

    self.stdout.write(self.style.SUCCESS(f"Historical market data import finished. Rows processed: {total_rows}."))


def parse_required_date(value: str, field_name: str) -> date:
  parsed = parse_date(value)
  if parsed is None:
    raise CommandError(f"{field_name} must use YYYY-MM-DD format.")
  return parsed


def parse_optional_date(value: str | None, field_name: str) -> date | None:
  if not value:
    return None
  return parse_required_date(value, field_name)
