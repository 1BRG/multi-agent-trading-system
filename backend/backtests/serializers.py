from rest_framework import serializers

from backtests.models import BacktestRun


class BacktestRunSerializer(serializers.ModelSerializer):
  user = serializers.PrimaryKeyRelatedField(read_only=True)

  class Meta:
    model = BacktestRun
    fields = (
        "id",
        "user",
        "strategy",
        "stock",
        "start_date",
        "end_date",
        "initial_cash",
        "status",
        "metrics",
        "equity_curve",
        "trades",
        "error_message",
        "created_at",
        "updated_at",
    )
    read_only_fields = ("id", "user", "created_at", "updated_at")

  def validate_strategy(self, strategy):
    user = self.context["request"].user
    if strategy.owner_id != user.id and not strategy.is_public:
      raise serializers.ValidationError("You can only backtest your own or public strategies.")
    # Enforce that only APPROVED strategies can be backtested
    try:
      approved_value = strategy.__class__.Status.APPROVED
    except Exception:
      approved_value = "approved"

    if getattr(strategy, "status", None) != approved_value:
      raise serializers.ValidationError("Strategy must be approved before backtesting.")

    return strategy
