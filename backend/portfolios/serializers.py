from rest_framework import serializers

from portfolios.models import Portfolio, PortfolioHolding


class PortfolioHoldingSerializer(serializers.ModelSerializer):
  asset_symbol = serializers.CharField(source="asset.symbol", read_only=True)
  asset_name = serializers.CharField(source="asset.name", read_only=True)

  class Meta:
    model = PortfolioHolding
    fields = (
        "id",
        "portfolio",
        "asset",
        "asset_symbol",
        "asset_name",
        "target_weight",
        "quantity",
        "average_cost",
        "created_at",
        "updated_at",
    )
    read_only_fields = ("id", "asset_symbol", "asset_name", "created_at", "updated_at")

  def validate_portfolio(self, portfolio):
    user = self.context["request"].user
    if portfolio.user_id != user.id:
      raise serializers.ValidationError("You can only edit holdings from your own portfolios.")
    return portfolio

  def validate_asset(self, asset):
    if not asset.is_active:
      raise serializers.ValidationError("Asset is inactive.")
    return asset

  def validate(self, attrs):
    portfolio = attrs.get("portfolio") or getattr(self.instance, "portfolio", None)
    asset = attrs.get("asset") or getattr(self.instance, "asset", None)
    if portfolio is None or asset is None:
      return attrs

    queryset = PortfolioHolding.objects.filter(portfolio=portfolio, asset=asset)
    if self.instance is not None:
      queryset = queryset.exclude(pk=self.instance.pk)
    if queryset.exists():
      raise serializers.ValidationError("This asset already exists in the portfolio.")
    return attrs


class NestedPortfolioHoldingSerializer(serializers.ModelSerializer):
  asset_symbol = serializers.CharField(source="asset.symbol", read_only=True)
  asset_name = serializers.CharField(source="asset.name", read_only=True)

  class Meta:
    model = PortfolioHolding
    fields = (
        "id",
        "asset",
        "asset_symbol",
        "asset_name",
        "target_weight",
        "quantity",
        "average_cost",
        "created_at",
        "updated_at",
    )


class PortfolioSerializer(serializers.ModelSerializer):
  user = serializers.PrimaryKeyRelatedField(read_only=True)
  holdings = NestedPortfolioHoldingSerializer(many=True, read_only=True)

  class Meta:
    model = Portfolio
    fields = (
        "id",
        "user",
        "name",
        "cash",
        "base_currency",
        "description",
        "holdings",
        "created_at",
        "updated_at",
    )
    read_only_fields = ("id", "user", "holdings", "created_at", "updated_at")

  def validate_name(self, name):
    request = self.context["request"]
    queryset = Portfolio.objects.filter(user=request.user, name=name)
    if self.instance is not None:
      queryset = queryset.exclude(pk=self.instance.pk)
    if queryset.exists():
      raise serializers.ValidationError("You already have a portfolio with this name.")
    return name
