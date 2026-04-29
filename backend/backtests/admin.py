from django.contrib import admin

from backtests.models import BacktestRun


@admin.register(BacktestRun)
class BacktestRunAdmin(admin.ModelAdmin):
  list_display = ("id", "user", "strategy", "stock", "status", "created_at")
  list_filter = ("status", "stock")
  search_fields = ("user__username", "user__email", "strategy__name", "stock__symbol")
