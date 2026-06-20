from rest_framework import serializers

from market.models import Asset, AssetPrice


class AssetSerializer(serializers.ModelSerializer):
  latest_price = serializers.SerializerMethodField()

  class Meta:
    model = Asset
    fields = (
        "id",
        "symbol",
        "name",
        "asset_type",
        "sector",
        "exchange",
        "currency",
        "is_active",
        "latest_price",
        "created_at",
        "updated_at",
    )
    read_only_fields = ("id", "created_at", "updated_at")

  def get_latest_price(self, asset):
    if hasattr(asset, "prefetched_latest_price"):
      latest_price = asset.prefetched_latest_price
      if latest_price is None:
        return None
      return ChartAssetPriceSerializer(latest_price).data

    latest_price = asset.prices.order_by("-date").first()
    if latest_price is None:
      return None
    return ChartAssetPriceSerializer(latest_price).data


class AssetPriceSerializer(serializers.ModelSerializer):
  symbol = serializers.CharField(source="asset.symbol", read_only=True)
  asset_id = serializers.IntegerField(source="asset.id", read_only=True)

  class Meta:
    model = AssetPrice
    fields = (
        "id",
        "asset",
        "asset_id",
        "symbol",
        "date",
        "open",
        "high",
        "low",
        "close",
        "adjusted_close",
        "volume",
        "source",
        "created_at",
        "updated_at",
    )
    read_only_fields = ("id", "asset_id", "symbol", "created_at", "updated_at")


class ChartAssetPriceSerializer(serializers.ModelSerializer):
  symbol = serializers.CharField(source="asset.symbol", read_only=True)
  asset_id = serializers.IntegerField(source="asset.id", read_only=True)

  class Meta:
    model = AssetPrice
    fields = (
        "asset_id",
        "symbol",
        "date",
        "open",
        "high",
        "low",
        "close",
        "adjusted_close",
        "volume",
        "source",
    )


# Backwards-compatible aliases for code that still imports stock serializers.
StockSerializer = AssetSerializer
StockPriceSerializer = AssetPriceSerializer
