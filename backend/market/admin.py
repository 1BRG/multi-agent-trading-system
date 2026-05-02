from django.contrib import admin

from market.models import Asset, AssetPrice


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
  list_display = ("symbol", "name", "asset_type", "sector", "exchange", "currency", "is_active")
  list_filter = ("asset_type", "is_active")
  search_fields = ("symbol", "name", "sector")


@admin.register(AssetPrice)
class AssetPriceAdmin(admin.ModelAdmin):
  list_display = ("asset", "date", "close", "volume", "source")
  list_filter = ("asset", "source")
  search_fields = ("asset__symbol",)
