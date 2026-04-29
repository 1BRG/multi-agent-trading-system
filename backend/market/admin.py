from django.contrib import admin

from market.models import Stock, StockPrice


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
  list_display = ("symbol", "name", "sector", "exchange", "currency", "is_active")
  search_fields = ("symbol", "name", "sector")


@admin.register(StockPrice)
class StockPriceAdmin(admin.ModelAdmin):
  list_display = ("stock", "date", "close", "volume")
  list_filter = ("stock",)
  search_fields = ("stock__symbol",)
