from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from typing import Iterable

import yfinance as yf
from django.utils import timezone

from market.models import Asset, AssetPrice

DEFAULT_HISTORY_START_DATE = date(2010, 1, 1)
DEFAULT_SOURCE = "yahoo"


@dataclass(frozen=True)
class SupportedAsset:
  symbol: str
  name: str
  asset_type: str
  exchange: str = ""
  currency: str = "USD"
  sector: str = ""


SUPPORTED_ASSETS: tuple[SupportedAsset, ...] = (
    SupportedAsset("AAPL", "Apple Inc.", Asset.AssetType.STOCK, "NASDAQ", "USD", "Technology"),
    SupportedAsset("MSFT", "Microsoft Corp.", Asset.AssetType.STOCK, "NASDAQ", "USD", "Technology"),
    SupportedAsset("GOOGL", "Alphabet Inc.", Asset.AssetType.STOCK, "NASDAQ", "USD", "Communication Services"),
    SupportedAsset("AMZN", "Amazon.com Inc.", Asset.AssetType.STOCK, "NASDAQ", "USD", "Consumer Discretionary"),
    SupportedAsset("NVDA", "NVIDIA Corp.", Asset.AssetType.STOCK, "NASDAQ", "USD", "Technology"),
    SupportedAsset("TSLA", "Tesla Inc.", Asset.AssetType.STOCK, "NASDAQ", "USD", "Consumer Discretionary"),
    SupportedAsset("META", "Meta Platforms Inc.", Asset.AssetType.STOCK, "NASDAQ", "USD", "Communication Services"),
    SupportedAsset("JPM", "JPMorgan Chase & Co.", Asset.AssetType.STOCK, "NYSE", "USD", "Financial Services"),
    SupportedAsset("KO", "The Coca-Cola Co.", Asset.AssetType.STOCK, "NYSE", "USD", "Consumer Defensive"),
    SupportedAsset("WMT", "Walmart Inc.", Asset.AssetType.STOCK, "NYSE", "USD", "Consumer Defensive"),
    SupportedAsset("SPY", "SPDR S&P 500 ETF Trust", Asset.AssetType.ETF, "NYSE Arca"),
    SupportedAsset("QQQ", "Invesco QQQ Trust", Asset.AssetType.ETF, "NASDAQ"),
    SupportedAsset("GLD", "SPDR Gold Shares", Asset.AssetType.ETF, "NYSE Arca"),
    SupportedAsset("GC=F", "Gold Futures", Asset.AssetType.COMMODITY, "COMEX"),
)


def seed_supported_assets(symbols: Iterable[str] | None = None) -> list[Asset]:
  requested_symbols = {symbol.upper() for symbol in symbols} if symbols else None
  assets = []

  for supported_asset in SUPPORTED_ASSETS:
    if requested_symbols and supported_asset.symbol.upper() not in requested_symbols:
      continue

    asset, _ = Asset.objects.update_or_create(
        symbol=supported_asset.symbol,
        defaults={
            "name": supported_asset.name,
            "asset_type": supported_asset.asset_type,
            "sector": supported_asset.sector,
            "exchange": supported_asset.exchange,
            "currency": supported_asset.currency,
            "is_active": True,
        },
    )
    assets.append(asset)

  return assets


def import_historical_prices(
    asset: Asset,
    start_date: date = DEFAULT_HISTORY_START_DATE,
    end_date: date | None = None,
    source: str = DEFAULT_SOURCE,
) -> int:
  end_date = end_date or timezone.localdate()
  if start_date > end_date:
    return 0

  frame = yf.download(
      asset.symbol,
      start=start_date.isoformat(),
      end=(end_date + timedelta(days=1)).isoformat(),
      auto_adjust=False,
      progress=False,
      actions=False,
      threads=False,
  )
  if frame.empty:
    return 0
  frame = normalize_download_frame(frame, asset.symbol)

  imported_count = 0
  for index, row in frame.iterrows():
    price_date = index.date()
    price_payload = build_price_payload(row, source)
    if price_payload is None:
      continue

    AssetPrice.objects.update_or_create(
        asset=asset,
        date=price_date,
        defaults=price_payload,
    )
    imported_count += 1

  return imported_count


def normalize_download_frame(frame, symbol: str):
  if getattr(frame.columns, "nlevels", 1) <= 1:
    return frame

  column_symbols = set(str(value).upper() for value in frame.columns.get_level_values(-1))
  if symbol.upper() in column_symbols:
    return frame.xs(symbol, axis=1, level=-1)

  frame = frame.copy()
  frame.columns = frame.columns.get_level_values(0)
  return frame


def update_missing_prices(asset: Asset, source: str = DEFAULT_SOURCE) -> int:
  latest_date = AssetPrice.objects.filter(asset=asset).order_by("-date").values_list("date", flat=True).first()
  start_date = latest_date + timedelta(days=1) if latest_date else DEFAULT_HISTORY_START_DATE
  return import_historical_prices(asset=asset, start_date=start_date, source=source)


def build_price_payload(row, source: str) -> dict | None:
  open_price = decimal_or_none(row.get("Open"))
  high_price = decimal_or_none(row.get("High"))
  low_price = decimal_or_none(row.get("Low"))
  close_price = decimal_or_none(row.get("Close"))
  adjusted_close = decimal_or_none(row.get("Adj Close")) or close_price
  volume_value = row.get("Volume")
  volume = int(volume_value) if volume_value == volume_value else 0

  if not all([open_price, high_price, low_price, close_price]):
    return None

  return {
      "open": open_price,
      "high": high_price,
      "low": low_price,
      "close": close_price,
      "adjusted_close": adjusted_close,
      "volume": volume,
      "source": source,
  }


def decimal_or_none(value) -> Decimal | None:
  try:
    if value is None or value != value:
      return None
    return Decimal(str(value)).quantize(Decimal("0.000001"))
  except (InvalidOperation, TypeError, ValueError):
    return None
