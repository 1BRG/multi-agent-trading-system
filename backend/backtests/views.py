from rest_framework import viewsets

from backtests.models import BacktestRun
from backtests.serializers import BacktestRunSerializer


class BacktestRunViewSet(viewsets.ModelViewSet):
  serializer_class = BacktestRunSerializer

  def get_queryset(self):
    return BacktestRun.objects.filter(user=self.request.user).select_related("user", "strategy", "stock")

  def perform_create(self, serializer):
    serializer.save(user=self.request.user)
