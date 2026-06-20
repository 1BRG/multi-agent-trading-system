from rest_framework import exceptions, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from conversations.models import ChatMessage, ChatThread, DebateMessage, DebateSession, StockSignal
from conversations.serializers import (
    ChatMessageSerializer,
    ChatThreadSerializer,
    DebateMessageSerializer,
    DebateSessionDetailSerializer,
    DebateSessionSerializer,
    StockSignalSerializer,
)
from market.models import Asset


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

  def get_serializer_class(self):
    if self.action == "retrieve":
      return DebateSessionDetailSerializer
    return DebateSessionSerializer

  def get_queryset(self):
    return DebateSession.objects.filter(user=self.request.user).select_related("stock", "user")

  def perform_create(self, serializer):
    serializer.save(user=self.request.user)

  @action(detail=False, methods=["post"])
  def run_debate(self, request):
    """
    POST /debates/run_debate
    Body: { "ticker": "AAPL" }

    Runs a full 5-round Bull/Bear/Judge debate for the given stock
    and returns the debate session with all messages and the final signal.
    """
    ticker = request.data.get("ticker", "").strip().upper()
    if not ticker:
      return Response(
        {"detail": "Please provide a ticker symbol."},
        status=status.HTTP_400_BAD_REQUEST,
      )

    try:
      asset = Asset.objects.get(symbol=ticker, is_active=True)
    except Asset.DoesNotExist:
      return Response(
        {"detail": f"Ticker '{ticker}' is not a supported asset."},
        status=status.HTTP_400_BAD_REQUEST,
      )

    # Create the debate session
    session = DebateSession.objects.create(
      user=request.user,
      stock=asset,
      topic=f"Bull vs Bear: {ticker}",
      status=DebateSession.Status.PENDING,
    )

    try:
      from conversations.debate_service import run_debate as execute_debate

      execute_debate(session, asset)
    except ValueError as exc:
      return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as exc:
      return Response(
        {"detail": f"Debate failed: {str(exc)}"},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
      )

    # Reload session with messages and signal
    session.refresh_from_db()
    serializer = DebateSessionDetailSerializer(session)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


class DebateMessageViewSet(viewsets.ModelViewSet):
  serializer_class = DebateMessageSerializer

  def get_queryset(self):
    return DebateMessage.objects.filter(session__user=self.request.user).select_related("session")

  def perform_create(self, serializer):
    session = serializer.validated_data["session"]
    if session.user_id != self.request.user.id:
      raise exceptions.PermissionDenied("You can only add messages to your own debates.")
    serializer.save()


class StockSignalViewSet(viewsets.ReadOnlyModelViewSet):
  """Read-only access to stock signals for the current user."""

  serializer_class = StockSignalSerializer
  permission_classes = [permissions.IsAuthenticated]

  def get_queryset(self):
    return StockSignal.objects.filter(user=self.request.user).select_related("asset", "debate_session")
