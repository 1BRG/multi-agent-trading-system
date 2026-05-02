from django.utils.dateparse import parse_date
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from market.models import Asset, AssetPrice
from market.serializers import AssetPriceSerializer, AssetSerializer, ChartAssetPriceSerializer


class IsAdminOrReadOnly(permissions.BasePermission):
  def has_permission(self, request, view):
    if request.method in permissions.SAFE_METHODS:
      return True
    return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class AssetViewSet(viewsets.ModelViewSet):
  permission_classes = [IsAdminOrReadOnly]
  serializer_class = AssetSerializer
  queryset = Asset.objects.all()
  search_fields = ("symbol", "name", "sector", "asset_type")


class AssetPriceViewSet(viewsets.ModelViewSet):
  permission_classes = [IsAdminOrReadOnly]
  serializer_class = AssetPriceSerializer

  def get_queryset(self):
    queryset = AssetPrice.objects.select_related("asset")
    symbol = self.request.query_params.get("symbol")
    if symbol:
      queryset = queryset.filter(asset__symbol__iexact=symbol)
    return queryset


class AssetListAPIView(APIView):
  permission_classes = [permissions.AllowAny]

  def get(self, request):
    assets = Asset.objects.filter(is_active=True).order_by("symbol")
    return Response(AssetSerializer(assets, many=True).data)


class AssetPricesAPIView(APIView):
  permission_classes = [permissions.AllowAny]

  def get(self, request, symbol: str):
    asset = Asset.objects.filter(symbol__iexact=symbol).first()
    if not asset:
      return Response({"detail": "Asset not found."}, status=status.HTTP_404_NOT_FOUND)

    queryset = AssetPrice.objects.filter(asset=asset).select_related("asset").order_by("date")

    start_date = parse_optional_date(request.query_params.get("start"), "start")
    if isinstance(start_date, Response):
      return start_date
    if start_date:
      queryset = queryset.filter(date__gte=start_date)

    end_date = parse_optional_date(request.query_params.get("end"), "end")
    if isinstance(end_date, Response):
      return end_date
    if end_date:
      queryset = queryset.filter(date__lte=end_date)

    return Response(
        {
            "asset": AssetSerializer(asset).data,
            "prices": ChartAssetPriceSerializer(queryset, many=True).data,
        }
    )


def parse_optional_date(value: str | None, field_name: str):
  if not value:
    return None

  parsed = parse_date(value)
  if parsed is None:
    return Response(
        {field_name: "Expected date format YYYY-MM-DD."},
        status=status.HTTP_400_BAD_REQUEST,
    )
  return parsed


# Backwards-compatible class names for existing URL imports.
StockViewSet = AssetViewSet
StockPriceViewSet = AssetPriceViewSet
