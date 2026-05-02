from django.db import migrations


SUPPORTED_ASSETS = (
    ("AAPL", "Apple Inc.", "stock", "NASDAQ", "USD", "Technology"),
    ("MSFT", "Microsoft Corp.", "stock", "NASDAQ", "USD", "Technology"),
    ("GOOGL", "Alphabet Inc.", "stock", "NASDAQ", "USD", "Communication Services"),
    ("AMZN", "Amazon.com Inc.", "stock", "NASDAQ", "USD", "Consumer Discretionary"),
    ("NVDA", "NVIDIA Corp.", "stock", "NASDAQ", "USD", "Technology"),
    ("TSLA", "Tesla Inc.", "stock", "NASDAQ", "USD", "Consumer Discretionary"),
    ("META", "Meta Platforms Inc.", "stock", "NASDAQ", "USD", "Communication Services"),
    ("JPM", "JPMorgan Chase & Co.", "stock", "NYSE", "USD", "Financial Services"),
    ("KO", "The Coca-Cola Co.", "stock", "NYSE", "USD", "Consumer Defensive"),
    ("WMT", "Walmart Inc.", "stock", "NYSE", "USD", "Consumer Defensive"),
    ("SPY", "SPDR S&P 500 ETF Trust", "etf", "NYSE Arca", "USD", ""),
    ("QQQ", "Invesco QQQ Trust", "etf", "NASDAQ", "USD", ""),
    ("GLD", "SPDR Gold Shares", "etf", "NYSE Arca", "USD", ""),
    ("GC=F", "Gold Futures", "commodity", "COMEX", "USD", ""),
)


def seed_supported_assets(apps, schema_editor):
    Asset = apps.get_model("market", "Asset")

    for symbol, name, asset_type, exchange, currency, sector in SUPPORTED_ASSETS:
        Asset.objects.update_or_create(
            symbol=symbol,
            defaults={
                "name": name,
                "asset_type": asset_type,
                "exchange": exchange,
                "currency": currency,
                "sector": sector,
                "is_active": True,
            },
        )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("market", "0003_delete_stock_delete_stockprice_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_supported_assets, noop_reverse),
    ]
