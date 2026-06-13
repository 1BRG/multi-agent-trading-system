from django.utils.dateparse import parse_date
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from market.models import Asset
from portfolios.models import Portfolio, PortfolioHolding
from portfolios.serializers import PortfolioHoldingSerializer, PortfolioSerializer, resolve_purchase_price


class PortfolioViewSet(viewsets.ModelViewSet):
  serializer_class = PortfolioSerializer

  def get_queryset(self):
    return (
        Portfolio.objects.filter(user=self.request.user)
        .prefetch_related("holdings__asset")
        .select_related("user")
    )

  def perform_create(self, serializer):
    serializer.save(user=self.request.user)


class PortfolioHoldingViewSet(viewsets.ModelViewSet):
  serializer_class = PortfolioHoldingSerializer

  def get_queryset(self):
    return PortfolioHolding.objects.filter(portfolio__user=self.request.user).select_related(
        "portfolio",
        "asset",
    )

  @action(detail=False, methods=["get"], url_path="resolve-price")
  def resolve_price(self, request):
    asset_id = request.query_params.get("asset")
    purchase_date_raw = request.query_params.get("purchase_date")
    requested_source = request.query_params.get(
        "price_source",
        PortfolioHolding.PriceSource.PREVIOUS_CLOSE,
    )

    if requested_source not in {
        PortfolioHolding.PriceSource.MARKET_CLOSE,
        PortfolioHolding.PriceSource.PREVIOUS_CLOSE,
    }:
      return Response(
          {"price_source": "Expected market_close or previous_close."},
          status=status.HTTP_400_BAD_REQUEST,
      )

    purchase_date = parse_date(purchase_date_raw or "")
    if purchase_date is None:
      return Response(
          {"purchase_date": "Expected date format YYYY-MM-DD."},
          status=status.HTTP_400_BAD_REQUEST,
      )

    asset = Asset.objects.filter(id=asset_id, is_active=True).first()
    if asset is None:
      return Response({"asset": "Active asset not found."}, status=status.HTTP_404_NOT_FOUND)

    try:
      price, resolved_source = resolve_purchase_price(asset, purchase_date, requested_source)
    except ValidationError as caught_error:
      detail = caught_error.detail
      return Response(detail, status=status.HTTP_400_BAD_REQUEST)

    return Response(
        {
            "asset": asset.id,
            "asset_symbol": asset.symbol,
            "purchase_date": purchase_date,
            "price_date": price.date,
            "price_source": resolved_source,
            "average_cost": f"{price.close:.6f}",
        }
    )
