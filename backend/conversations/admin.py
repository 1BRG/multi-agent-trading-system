from django.contrib import admin

from conversations.models import ChatMessage, ChatThread, DebateMessage, DebateSession


admin.site.register(ChatThread)
admin.site.register(ChatMessage)
admin.site.register(DebateSession)
admin.site.register(DebateMessage)
