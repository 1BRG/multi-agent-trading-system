from django.db import models


class Asset(models.Model):
  class AssetType(models.TextChoices):
    STOCK = "stock", "Stock"
    ETF = "etf", "ETF"
    COMMODITY = "commodity", "Commodity"

  symbol = models.CharField(max_length=24, unique=True)
  name = models.CharField(max_length=255)
  asset_type = models.CharField(max_length=20, choices=AssetType.choices, default=AssetType.STOCK)
  sector = models.CharField(max_length=100, blank=True)
  exchange = models.CharField(max_length=50, blank=True)
  currency = models.CharField(max_length=10, default="USD")
  is_active = models.BooleanField(default=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    db_table = "assets"
    ordering = ["symbol"]

  def save(self, *args, **kwargs):
    self.symbol = self.symbol.strip().upper()
    self.currency = self.currency.strip().upper() or "USD"
    super().save(*args, **kwargs)

  def __str__(self) -> str:
    return f"{self.symbol} - {self.name}"


class AssetPrice(models.Model):
  asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="prices")
  date = models.DateField()
  open = models.DecimalField(max_digits=18, decimal_places=6)
  high = models.DecimalField(max_digits=18, decimal_places=6)
  low = models.DecimalField(max_digits=18, decimal_places=6)
  close = models.DecimalField(max_digits=18, decimal_places=6)
  adjusted_close = models.DecimalField(max_digits=18, decimal_places=6, null=True, blank=True)
  volume = models.BigIntegerField(default=0)
  source = models.CharField(max_length=50, default="yahoo")
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    db_table = "asset_prices"
    constraints = [
        models.UniqueConstraint(fields=["asset", "date"], name="asset_prices_asset_date_unique"),
    ]
    indexes = [
        models.Index(fields=["asset", "date"], name="asset_prices_asset_date_idx"),
    ]
    ordering = ["asset__symbol", "date"]

  def __str__(self) -> str:
    return f"{self.asset.symbol} {self.date}"


# Backwards-compatible aliases while older modules are migrated.
Stock = Asset
StockPrice = AssetPrice
