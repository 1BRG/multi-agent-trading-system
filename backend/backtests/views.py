from rest_framework import viewsets

from backtests.engine import run_backtest
from backtests.models import BacktestRun
from backtests.serializers import BacktestRunSerializer


class BacktestRunViewSet(viewsets.ModelViewSet):
  serializer_class = BacktestRunSerializer

  def get_queryset(self):
    return BacktestRun.objects.filter(user=self.request.user).select_related("user", "strategy", "stock")

  def perform_create(self, serializer):
    run = serializer.save(user=self.request.user, status=BacktestRun.Status.RUNNING)
    try:
      result = run_backtest(
          strategy=run.strategy,
          stock=run.stock,
          start_date=run.start_date,
          end_date=run.end_date,
          initial_cash=run.initial_cash,
      )
      run.status = BacktestRun.Status.COMPLETED
      run.metrics = result["metrics"]
      run.equity_curve = result["equity_curve"]
      run.trades = result["trades"]
      run.error_message = ""
    except Exception as exc:
      run.status = BacktestRun.Status.FAILED
      run.metrics = {}
      run.equity_curve = []
      run.trades = []
      run.error_message = str(exc)
    run.save(update_fields=["status", "metrics", "equity_curve", "trades", "error_message", "updated_at"])
