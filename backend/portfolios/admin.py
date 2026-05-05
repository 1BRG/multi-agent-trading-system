from django.contrib import admin

from portfolios.models import Portfolio, PortfolioHolding


class PortfolioHoldingInline(admin.TabularInline):
  model = PortfolioHolding
  extra = 0


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
  list_display = ("name", "user", "cash", "base_currency", "created_at", "updated_at")
  search_fields = ("name", "user__username", "user__email")
  list_filter = ("base_currency",)
  inlines = (PortfolioHoldingInline,)


@admin.register(PortfolioHolding)
class PortfolioHoldingAdmin(admin.ModelAdmin):
  list_display = ("portfolio", "asset", "target_weight", "quantity", "average_cost")
  search_fields = ("portfolio__name", "asset__symbol", "asset__name")
