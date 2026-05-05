from rest_framework import viewsets

from portfolios.models import Portfolio, PortfolioHolding
from portfolios.serializers import PortfolioHoldingSerializer, PortfolioSerializer


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
