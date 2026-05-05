from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Portfolio(models.Model):
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="portfolios")
  name = models.CharField(max_length=255)
  cash = models.DecimalField(max_digits=14, decimal_places=2, default=0)
  base_currency = models.CharField(max_length=10, default="USD")
  description = models.TextField(blank=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    db_table = "portfolios"
    constraints = [
        models.UniqueConstraint(fields=["user", "name"], name="portfolio_user_name_unique"),
    ]
    indexes = [
        models.Index(fields=["user", "name"], name="portfolio_user_name_idx"),
    ]
    ordering = ["name"]

  def save(self, *args, **kwargs):
    self.base_currency = self.base_currency.strip().upper() or "USD"
    super().save(*args, **kwargs)

  def __str__(self) -> str:
    return self.name


class PortfolioHolding(models.Model):
  portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="holdings")
  asset = models.ForeignKey("market.Asset", on_delete=models.CASCADE, related_name="portfolio_holdings")
  target_weight = models.DecimalField(
      max_digits=6,
      decimal_places=4,
      default=0,
      validators=[MinValueValidator(0), MaxValueValidator(1)],
  )
  quantity = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
  average_cost = models.DecimalField(max_digits=18, decimal_places=6, null=True, blank=True)
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
    ]
    indexes = [
        models.Index(fields=["portfolio", "asset"], name="pf_hold_port_asset_idx"),
    ]
    ordering = ["portfolio__name", "asset__symbol"]

  def __str__(self) -> str:
    return f"{self.portfolio} - {self.asset.symbol}"
