from rest_framework import serializers

from market.models import Stock, StockPrice


class StockSerializer(serializers.ModelSerializer):
  class Meta:
    model = Stock
    fields = (
        "id",
        "symbol",
        "name",
        "sector",
        "exchange",
        "currency",
        "is_active",
        "created_at",
        "updated_at",
    )
    read_only_fields = ("id", "created_at", "updated_at")


class StockPriceSerializer(serializers.ModelSerializer):
  symbol = serializers.CharField(source="stock.symbol", read_only=True)

  class Meta:
    model = StockPrice
    fields = (
        "id",
        "stock",
        "symbol",
        "date",
        "open",
        "high",
        "low",
        "close",
        "adjusted_close",
        "volume",
        "created_at",
    )
    read_only_fields = ("id", "symbol", "created_at")
