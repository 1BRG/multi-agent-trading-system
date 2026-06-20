from decimal import Decimal

from django.db.models import Sum
from rest_framework import serializers

from market.models import AssetPrice
from portfolios.models import Portfolio, PortfolioHolding


SUPPORTED_PORTFOLIO_CURRENCIES = {"USD"}
AUTOMATIC_PRICE_SOURCES = {
    PortfolioHolding.PriceSource.MARKET_CLOSE,
    PortfolioHolding.PriceSource.PREVIOUS_CLOSE,
}


def resolve_purchase_price(asset, purchase_date, requested_source):
  if requested_source == PortfolioHolding.PriceSource.MARKET_CLOSE:
    price = AssetPrice.objects.filter(asset=asset, date=purchase_date).first()
    if price is None:
      raise serializers.ValidationError(
          {
              "purchase_date": (
                  "No stored market price exists for this date. "
                  "Use previous close or custom price instead."
              )
          }
      )
    return price, PortfolioHolding.PriceSource.MARKET_CLOSE

  price = AssetPrice.objects.filter(asset=asset, date__lte=purchase_date).order_by("-date").first()
  if price is None:
    raise serializers.ValidationError(
        {"purchase_date": "No stored market price exists on or before this date."}
    )

  resolved_source = (
      PortfolioHolding.PriceSource.MARKET_CLOSE
      if price.date == purchase_date
      else PortfolioHolding.PriceSource.PREVIOUS_CLOSE
  )
  return price, resolved_source


def normalized_decimal_string(value):
  if value is None:
    return None
  return str(value).strip()


class PortfolioHoldingSerializer(serializers.ModelSerializer):
  asset_symbol = serializers.CharField(source="asset.symbol", read_only=True)
  asset_name = serializers.CharField(source="asset.name", read_only=True)
  asset_currency = serializers.CharField(source="asset.currency", read_only=True)

  class Meta:
    model = PortfolioHolding
    fields = (
        "id",
        "portfolio",
        "asset",
        "asset_symbol",
        "asset_name",
        "asset_currency",
        "target_weight",
        "quantity",
        "average_cost",
        "purchase_date",
        "price_date",
        "price_source",
        "created_at",
        "updated_at",
    )
    read_only_fields = (
        "id",
        "asset_symbol",
        "asset_name",
        "asset_currency",
        "price_date",
        "created_at",
        "updated_at",
    )
    extra_kwargs = {
        "target_weight": {"required": False},
    }

  def validate_portfolio(self, portfolio):
    user = self.context["request"].user
    if portfolio.user_id != user.id:
      raise serializers.ValidationError("You can only edit holdings from your own portfolios.")
    return portfolio

  def validate_asset(self, asset):
    if not asset.is_active:
      raise serializers.ValidationError("Asset is inactive.")
    return asset

  def validate_quantity(self, quantity):
    if quantity is not None and quantity <= 0:
      raise serializers.ValidationError("Quantity must be greater than 0.")
    return quantity

  def validate_average_cost(self, average_cost):
    if average_cost is not None and average_cost <= 0:
      raise serializers.ValidationError("Average cost must be greater than 0.")
    return average_cost

  def validate(self, attrs):
    portfolio = attrs.get("portfolio") or getattr(self.instance, "portfolio", None)
    asset = attrs.get("asset") or getattr(self.instance, "asset", None)
    if portfolio is None or asset is None:
      return attrs

    if asset.currency and portfolio.base_currency and asset.currency.upper() != portfolio.base_currency.upper():
      raise serializers.ValidationError(
          {"asset": "Asset currency must match the portfolio base currency."}
      )

    queryset = PortfolioHolding.objects.filter(portfolio=portfolio, asset=asset)
    if self.instance is not None:
      queryset = queryset.exclude(pk=self.instance.pk)
    if queryset.exists():
      raise serializers.ValidationError("This asset already exists in the portfolio.")

    target_weight = attrs.get("target_weight")
    if target_weight is None:
      target_weight = getattr(self.instance, "target_weight", Decimal("0"))
    existing_weight = (
        PortfolioHolding.objects.filter(portfolio=portfolio)
        .exclude(pk=getattr(self.instance, "pk", None))
        .aggregate(total=Sum("target_weight"))["total"]
        or Decimal("0")
    )
    if existing_weight + target_weight > Decimal("1"):
      remaining_weight = max(Decimal("0"), Decimal("1") - existing_weight)
      raise serializers.ValidationError(
          {
              "target_weight": (
                  f"Target allocation exceeds 100%. Remaining allocation is "
                  f"{remaining_weight * Decimal('100'):.2f}%."
              )
          }
      )

    self._validate_price_basis(attrs, asset)
    return attrs

  def _validate_price_basis(self, attrs, asset):
    raw_data = getattr(self, "initial_data", {}) or {}
    source = attrs.get(
        "price_source",
        getattr(self.instance, "price_source", PortfolioHolding.PriceSource.UNKNOWN),
    )

    if "price_date" in raw_data and normalized_decimal_string(raw_data.get("price_date")):
      raise serializers.ValidationError({"price_date": "Price date is calculated by the server."})

    raw_average_cost = normalized_decimal_string(raw_data.get("average_cost"))
    raw_purchase_date = str(raw_data.get("purchase_date", "")).strip()

    if source in AUTOMATIC_PRICE_SOURCES:
      purchase_date = attrs.get("purchase_date") or getattr(self.instance, "purchase_date", None)
      if purchase_date is None:
        raise serializers.ValidationError(
            {"purchase_date": "Purchase date is required for market price lookup."}
        )
      if raw_average_cost:
        raise serializers.ValidationError(
            {"average_cost": "Average cost is calculated from market data for this price mode."}
        )

      price, resolved_source = resolve_purchase_price(asset, purchase_date, source)
      attrs["average_cost"] = price.close
      attrs["price_date"] = price.date
      attrs["price_source"] = resolved_source
      return

    if source == PortfolioHolding.PriceSource.MANUAL:
      average_cost = attrs.get("average_cost") or getattr(self.instance, "average_cost", None)
      if average_cost is None:
        raise serializers.ValidationError({"average_cost": "Custom price is required."})
      if raw_purchase_date:
        raise serializers.ValidationError(
            {"purchase_date": "Leave purchase date empty when using a custom price."}
        )
      attrs["purchase_date"] = None
      attrs["price_date"] = None
      return

    if source == PortfolioHolding.PriceSource.UNKNOWN:
      if raw_average_cost:
        raise serializers.ValidationError(
            {"average_cost": "Use manual price mode when entering a custom price."}
        )
      if raw_purchase_date:
        raise serializers.ValidationError(
            {"purchase_date": "Use market price mode when entering a purchase date."}
        )
      attrs["average_cost"] = None
      attrs["purchase_date"] = None
      attrs["price_date"] = None
      return

    raise serializers.ValidationError({"price_source": "Unsupported price source."})


class NestedPortfolioHoldingSerializer(serializers.ModelSerializer):
  asset_symbol = serializers.CharField(source="asset.symbol", read_only=True)
  asset_name = serializers.CharField(source="asset.name", read_only=True)
  asset_currency = serializers.CharField(source="asset.currency", read_only=True)

  class Meta:
    model = PortfolioHolding
    fields = (
        "id",
        "asset",
        "asset_symbol",
        "asset_name",
        "asset_currency",
        "target_weight",
        "quantity",
        "average_cost",
        "purchase_date",
        "price_date",
        "price_source",
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
    name = name.strip()
    if not name:
      raise serializers.ValidationError("Portfolio name is required.")
    request = self.context["request"]
    queryset = Portfolio.objects.filter(user=request.user, name__iexact=name)
    if self.instance is not None:
      queryset = queryset.exclude(pk=self.instance.pk)
    if queryset.exists():
      raise serializers.ValidationError("You already have a portfolio with this name.")
    return name

  def validate_base_currency(self, base_currency):
    base_currency = base_currency.strip().upper()
    if base_currency not in SUPPORTED_PORTFOLIO_CURRENCIES:
      supported = ", ".join(sorted(SUPPORTED_PORTFOLIO_CURRENCIES))
      raise serializers.ValidationError(f"Unsupported portfolio currency. Use one of: {supported}.")
    return base_currency

  def validate_cash(self, cash):
    if cash < 0:
      raise serializers.ValidationError("Cash cannot be negative.")
    return cash

  def validate_base_currency(self, base_currency):
    base_currency = base_currency.strip().upper()
    if base_currency not in SUPPORTED_PORTFOLIO_CURRENCIES:
      raise serializers.ValidationError("Only USD portfolios are supported right now.")
    return base_currency

  def validate_description(self, description):
    description = description.strip()
    if len(description) > 500:
      raise serializers.ValidationError("Description cannot exceed 500 characters.")
    return description
