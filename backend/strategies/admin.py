from django.contrib import admin

from strategies.models import Strategy


@admin.register(Strategy)
class StrategyAdmin(admin.ModelAdmin):
  list_display = ("id", "name", "owner", "source", "is_public", "created_at")
  list_filter = ("source", "is_public")
  search_fields = ("name", "owner__username", "owner__email")
