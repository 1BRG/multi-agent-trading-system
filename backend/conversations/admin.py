from django.contrib import admin

from conversations.models import ChatMessage, ChatThread, DebateMessage, DebateSession, StockSignal

admin.site.register(ChatThread)
admin.site.register(ChatMessage)
admin.site.register(DebateSession)
admin.site.register(DebateMessage)


@admin.register(StockSignal)
class StockSignalAdmin(admin.ModelAdmin):
  list_display = ("asset", "action", "conviction", "user", "created_at")
  list_filter = ("action",)
  readonly_fields = ("created_at",)
