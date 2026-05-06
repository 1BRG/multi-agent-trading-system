from django.db.models import Q
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

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
    def generate_ai(self, request):
        """
        Endpoint: POST /strategies/generate_ai
        Payload: { "prompt": "user's trading idea here" }
        """
        prompt = request.data.get("prompt")
        if not prompt or not prompt.strip():
            return Response(
                {"detail": "Please provide a prompt to generate a strategy."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 1. Ask the AI to build the ruleset
            ai_output = generate_strategy_rules(prompt)
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
        serializer = self.get_serializer(data={
            "name": ai_output.get("name", f"AI Strategy: {prompt[:20]}..."),
            "description": ai_output.get("description", ""),
            "config": ai_output.get("config", {}),
            "source": Strategy.Source.AI,
            "is_public": False,
        })
        
        # 3. Validate and save
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)