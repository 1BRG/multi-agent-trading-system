from django.conf import settings
from django.db import models


class BacktestRun(models.Model):
  class Status(models.TextChoices):
    PENDING = "pending", "Pending"
    RUNNING = "running", "Running"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"

  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="backtest_runs")
  strategy = models.ForeignKey("strategies.Strategy", on_delete=models.CASCADE, related_name="backtest_runs")
  stock = models.ForeignKey("market.Asset", on_delete=models.CASCADE, related_name="backtest_runs")
  start_date = models.DateField()
  end_date = models.DateField()
  initial_cash = models.DecimalField(max_digits=14, decimal_places=2, default=10000)
  status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
  metrics = models.JSONField(default=dict, blank=True)
  equity_curve = models.JSONField(default=list, blank=True)
  trades = models.JSONField(default=list, blank=True)
  error_message = models.TextField(blank=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    indexes = [
        models.Index(fields=["user", "status"], name="backtest_user_status_idx"),
        models.Index(fields=["strategy", "stock"], name="backtest_strategy_stock_idx"),
    ]
    ordering = ["-created_at"]

  def __str__(self) -> str:
    return f"{self.strategy} on {self.stock}"
