from rest_framework import exceptions, viewsets

from conversations.models import ChatMessage, ChatThread, DebateMessage, DebateSession
from conversations.serializers import (
    ChatMessageSerializer,
    ChatThreadSerializer,
    DebateMessageSerializer,
    DebateSessionSerializer,
)


class ChatThreadViewSet(viewsets.ModelViewSet):
  serializer_class = ChatThreadSerializer

  def get_queryset(self):
    return ChatThread.objects.filter(user=self.request.user).select_related("stock", "user")

  def perform_create(self, serializer):
    serializer.save(user=self.request.user)


class ChatMessageViewSet(viewsets.ModelViewSet):
  serializer_class = ChatMessageSerializer

  def get_queryset(self):
    return ChatMessage.objects.filter(thread__user=self.request.user).select_related("thread")

  def perform_create(self, serializer):
    thread = serializer.validated_data["thread"]
    if thread.user_id != self.request.user.id:
      raise exceptions.PermissionDenied("You can only add messages to your own chats.")
    serializer.save()


class DebateSessionViewSet(viewsets.ModelViewSet):
  serializer_class = DebateSessionSerializer

  def get_queryset(self):
    return DebateSession.objects.filter(user=self.request.user).select_related("stock", "user")

  def perform_create(self, serializer):
    serializer.save(user=self.request.user)


class DebateMessageViewSet(viewsets.ModelViewSet):
  serializer_class = DebateMessageSerializer

  def get_queryset(self):
    return DebateMessage.objects.filter(session__user=self.request.user).select_related("session")

  def perform_create(self, serializer):
    session = serializer.validated_data["session"]
    if session.user_id != self.request.user.id:
      raise exceptions.PermissionDenied("You can only add messages to your own debates.")
    serializer.save()
