from django.core.management.base import BaseCommand, CommandError

from market.data_importer import seed_supported_assets, update_missing_prices


class Command(BaseCommand):
  help = "Update supported assets by downloading only dates missing after the latest stored date."

  def add_arguments(self, parser):
    parser.add_argument("--symbol", action="append", dest="symbols", help="Update only this symbol. Can be repeated.")

  def handle(self, *args, **options):
    assets = seed_supported_assets(options.get("symbols"))
    if not assets:
      raise CommandError("No supported assets matched the requested symbols.")

    total_rows = 0
    for asset in assets:
      imported_count = update_missing_prices(asset)
      total_rows += imported_count
      self.stdout.write(f"{asset.symbol}: imported/updated {imported_count} missing rows.")

    self.stdout.write(self.style.SUCCESS(f"Market data update finished. Rows processed: {total_rows}."))
