from rest_framework import permissions, viewsets

from market.models import Stock, StockPrice
from market.serializers import StockPriceSerializer, StockSerializer


class IsAdminOrReadOnly(permissions.BasePermission):
  def has_permission(self, request, view):
    if request.method in permissions.SAFE_METHODS:
      return True
    return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class StockViewSet(viewsets.ModelViewSet):
  permission_classes = [IsAdminOrReadOnly]
  serializer_class = StockSerializer
  queryset = Stock.objects.all()
  search_fields = ("symbol", "name", "sector")


class StockPriceViewSet(viewsets.ModelViewSet):
  permission_classes = [IsAdminOrReadOnly]
  serializer_class = StockPriceSerializer

  def get_queryset(self):
    queryset = StockPrice.objects.select_related("stock")
    symbol = self.request.query_params.get("symbol")
    if symbol:
      queryset = queryset.filter(stock__symbol__iexact=symbol)
    return queryset
