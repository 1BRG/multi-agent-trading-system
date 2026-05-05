from django.db.models import Q
from rest_framework import permissions
from rest_framework import viewsets

from strategies.models import Strategy
from strategies.serializers import StrategySerializer


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
