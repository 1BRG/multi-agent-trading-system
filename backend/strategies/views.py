from django.db.models import Q
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from conversations.models import ChatMessage
from strategies.models import Strategy
from strategies.serializers import StrategySerializer
from strategies.ai_service import generate_strategy_rules


class IsOwnerOrReadOnlyPublic(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS and (obj.is_public or obj.owner == request.user):
            return True
        return obj.owner == request.user


class StrategyViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnlyPublic]
    serializer_class = StrategySerializer

    def get_queryset(self):
        return Strategy.objects.filter(Q(owner=self.request.user) | Q(is_public=True)).select_related("owner")

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=["post"])
    @action(detail=False, methods=["post"])
    def generate_ai(self, request):
        prompt = request.data.get("prompt")
        thread_id = request.data.get("thread_id") # Get the thread_id from frontend

        if not prompt or not prompt.strip():
            return Response({"detail": "Provide a prompt."}, status=400)

        # 1. Reconstruct chat history
        messages_history = []
        if thread_id:
            # Fetch past messages from the DB to give the AI context
            past_messages = ChatMessage.objects.filter(thread_id=thread_id).order_by("created_at")
            for msg in past_messages:
                messages_history.append({"role": msg.role, "content": msg.content})
        
        # Add the current user prompt
        messages_history.append({"role": "user", "content": prompt})

        # 2. Ask the AI 
        try:
            ai_result = generate_strategy_rules(messages_history)
            ai_output = ai_result.get("parsed", {})
            raw_llm = ai_result.get("raw", "")
        except ValueError as e:
            # Catch our custom parsing/LLM errors from ai_service.py
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"detail": f"Unexpected error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # 2. Feed the AI's output through the strict serializer we built in Step 1
        # This guarantees that if the LLM hallucinates bad config variables,
        # the serializer will catch it and return a 400 Validation Error.
        # When an AI creates a strategy, save it as DRAFT and persist raw LLM output for audit.
        serializer = self.get_serializer(data={
            "name": ai_output.get("name", f"AI Strategy: {prompt[:20]}..."),
            "description": ai_output.get("description", ""),
            "config": ai_output.get("config", {}),
            "source": Strategy.Source.AI,
            "is_public": False,
            "status": Strategy.Status.DRAFT,
            "raw_llm_response": raw_llm,
        })
        
        # 3. Validate and save
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["patch"])
    def approve(self, request, pk=None):
        """PATCH /strategies/{id}/approve - mark a strategy as approved (owner only)"""
        strategy = self.get_object()
        
        if strategy.owner != request.user:
            return Response({"detail": "Only the owner can approve this strategy."}, status=status.HTTP_403_FORBIDDEN)

        # 1. Approve the strategy
        strategy.status = Strategy.Status.APPROVED
        strategy.save()

       
        chat_messages = ChatMessage.objects.filter(thread__user=request.user)
        for msg in chat_messages:
            if msg.metadata and msg.metadata.get("strategyId") == strategy.id:
                msg.metadata["strategyStatus"] = "approved"
                msg.save()

        serializer = self.get_serializer(strategy)
        return Response(serializer.data, status=status.HTTP_200_OK)