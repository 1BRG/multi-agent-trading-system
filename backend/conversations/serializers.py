from rest_framework import serializers

from conversations.models import ChatMessage, ChatThread, DebateMessage, DebateSession


class ChatThreadSerializer(serializers.ModelSerializer):
  user = serializers.PrimaryKeyRelatedField(read_only=True)

  class Meta:
    model = ChatThread
    fields = ("id", "user", "stock", "title", "created_at", "updated_at")
    read_only_fields = ("id", "user", "created_at", "updated_at")


class ChatMessageSerializer(serializers.ModelSerializer):
  class Meta:
    model = ChatMessage
    fields = ("id", "thread", "role", "content", "metadata", "created_at")
    read_only_fields = ("id", "created_at")


class DebateSessionSerializer(serializers.ModelSerializer):
  user = serializers.PrimaryKeyRelatedField(read_only=True)

  class Meta:
    model = DebateSession
    fields = ("id", "user", "stock", "topic", "status", "summary", "created_at", "updated_at")
    read_only_fields = ("id", "user", "created_at", "updated_at")


class DebateMessageSerializer(serializers.ModelSerializer):
  class Meta:
    model = DebateMessage
    fields = ("id", "session", "agent_name", "agent_role", "round_number", "content", "created_at")
    read_only_fields = ("id", "created_at")
