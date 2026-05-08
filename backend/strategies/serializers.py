from rest_framework import serializers
from strategies.models import Strategy

class StrategyConfigSerializer(serializers.Serializer):
    rebalance_frequency = serializers.ChoiceField(
        choices=["daily", "weekly", "monthly", "quarterly"],
        help_text="How often the portfolio is rebalanced."
    )
    ranking_metric = serializers.ChoiceField(
        choices=["conviction"], 
        help_text="Metric from Person 3 used to rank the universe."
    )
    portfolio_size = serializers.IntegerField(
        min_value=1, 
        max_value=500,
        help_text="Top N stocks to hold."
    )
    sizing = serializers.ChoiceField(
        choices=["equal_weight", "conviction_weighted"],
        help_text="How capital is allocated across the portfolio."
    )
    sector_cap_pct = serializers.IntegerField(
        min_value=1, 
        max_value=100,
        help_text="Maximum percentage allocation to a single sector."
    )
    exit_on_signal_flip = serializers.BooleanField(
        help_text="If True, exit position immediately if signal changes to SELL."
    )
    min_conviction_score = serializers.FloatField(
        min_value=0.0, 
        max_value=1.0, 
        help_text="Only buy stocks with a Judge conviction score above this."
    )

class StrategySerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Strategy
        fields = (
            "id",
            "owner",
            "name",
            "description",
            "config",
            "status",
            "raw_llm_response",
            "source",
            "is_public",
            "created_at",
            "updated_at",
        )
       
        read_only_fields = ("id", "owner", "created_at", "updated_at")

    def validate_config(self, value):
        if not value:
            return value
            
        config_serializer = StrategyConfigSerializer(data=value)
        if not config_serializer.is_valid():
            raise serializers.ValidationError(config_serializer.errors)
            
        return config_serializer.validated_data