from rest_framework import serializers

from conversations.models import ChatMessage, ChatThread, DebateMessage, DebateSession, StockSignal


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


class DebateMessageSerializer(serializers.ModelSerializer):
  class Meta:
    model = DebateMessage
    fields = ("id", "session", "agent_name", "agent_role", "round_number", "content", "created_at")
    read_only_fields = ("id", "created_at")


class StockSignalSerializer(serializers.ModelSerializer):
  ticker = serializers.CharField(source="asset.symbol", read_only=True)
  timestamp = serializers.DateTimeField(source="created_at", read_only=True)

  class Meta:
    model = StockSignal
    fields = (
      "id",
      "user",
      "asset",
      "ticker",
      "debate_session",
      "action",
      "conviction",
      "bull_thesis",
      "bear_thesis",
      "judge_reasoning",
      "timestamp",
    )
    read_only_fields = (
      "id",
      "user",
      "asset",
      "ticker",
      "debate_session",
      "action",
      "conviction",
      "bull_thesis",
      "bear_thesis",
      "judge_reasoning",
      "timestamp",
    )


class DebateSessionSerializer(serializers.ModelSerializer):
  user = serializers.PrimaryKeyRelatedField(read_only=True)

  class Meta:
    model = DebateSession
    fields = ("id", "user", "stock", "topic", "status", "summary", "created_at", "updated_at")
    read_only_fields = ("id", "user", "created_at", "updated_at")


class DebateSessionDetailSerializer(serializers.ModelSerializer):
  """Extended serializer that nests debate messages and the signal verdict."""

  user = serializers.PrimaryKeyRelatedField(read_only=True)
  messages = DebateMessageSerializer(many=True, read_only=True)
  signal = StockSignalSerializer(read_only=True)

  class Meta:
    model = DebateSession
    fields = (
      "id",
      "user",
      "stock",
      "topic",
      "status",
      "summary",
      "messages",
      "signal",
      "created_at",
      "updated_at",
    )
    read_only_fields = (
      "id",
      "user",
      "created_at",
      "updated_at",
    )
