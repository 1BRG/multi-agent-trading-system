from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Portfolio(models.Model):
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="portfolios")
  name = models.CharField(max_length=255)
  cash = models.DecimalField(max_digits=14, decimal_places=2, default=0, validators=[MinValueValidator(0)])
  base_currency = models.CharField(max_length=10, default="USD")
  description = models.TextField(blank=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    db_table = "portfolios"
    constraints = [
        models.UniqueConstraint(fields=["user", "name"], name="portfolio_user_name_unique"),
        models.CheckConstraint(check=models.Q(cash__gte=0), name="portfolio_cash_non_negative"),
    ]
    indexes = [
        models.Index(fields=["user", "name"], name="portfolio_user_name_idx"),
    ]
    ordering = ["name"]

  def save(self, *args, **kwargs):
    self.name = self.name.strip()
    self.base_currency = self.base_currency.strip().upper() or "USD"
    super().save(*args, **kwargs)

  def __str__(self) -> str:
    return self.name


class PortfolioHolding(models.Model):
  class PriceSource(models.TextChoices):
    MARKET_CLOSE = "market_close", "Market close"
    PREVIOUS_CLOSE = "previous_close", "Previous close"
    MANUAL = "manual", "Manual"
    UNKNOWN = "unknown", "Unknown"

  portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="holdings")
  asset = models.ForeignKey("market.Asset", on_delete=models.CASCADE, related_name="portfolio_holdings")
  target_weight = models.DecimalField(
      max_digits=6,
      decimal_places=4,
      default=0,
      validators=[MinValueValidator(0), MaxValueValidator(1)],
  )
  quantity = models.DecimalField(
      max_digits=20,
      decimal_places=8,
      null=True,
      blank=True,
      validators=[MinValueValidator(0)],
  )
  average_cost = models.DecimalField(
      max_digits=18,
      decimal_places=6,
      null=True,
      blank=True,
      validators=[MinValueValidator(0)],
  )
  purchase_date = models.DateField(null=True, blank=True)
  price_date = models.DateField(null=True, blank=True)
  price_source = models.CharField(
      max_length=20,
      choices=PriceSource.choices,
      default=PriceSource.UNKNOWN,
  )
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    db_table = "portfolio_holdings"
    constraints = [
        models.UniqueConstraint(
            fields=["portfolio", "asset"],
            name="pf_hold_port_asset_uniq",
        ),
        models.CheckConstraint(
            check=models.Q(target_weight__gte=0) & models.Q(target_weight__lte=1),
            name="pf_hold_weight_range",
        ),
        models.CheckConstraint(
            check=models.Q(quantity__isnull=True) | models.Q(quantity__gte=0),
            name="pf_hold_quantity_non_negative",
        ),
        models.CheckConstraint(
            check=models.Q(average_cost__isnull=True) | models.Q(average_cost__gte=0),
            name="pf_hold_average_cost_non_negative",
        ),
        models.CheckConstraint(
            check=models.Q(price_date__isnull=True)
            | (models.Q(purchase_date__isnull=False) & models.Q(price_date__lte=models.F("purchase_date"))),
            name="pf_hold_price_date_not_after_purchase",
        ),
    ]
    indexes = [
        models.Index(fields=["portfolio", "asset"], name="pf_hold_port_asset_idx"),
    ]
    ordering = ["portfolio__name", "asset__symbol"]

  def __str__(self) -> str:
    return f"{self.portfolio} - {self.asset.symbol}"
