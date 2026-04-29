from rest_framework import serializers

from strategies.models import Strategy


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
        "source",
        "is_public",
        "created_at",
        "updated_at",
    )
    read_only_fields = ("id", "owner", "created_at", "updated_at")
