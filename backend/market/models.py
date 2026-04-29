from django.db import models


class Stock(models.Model):
  symbol = models.CharField(max_length=16, unique=True)
  name = models.CharField(max_length=255)
  sector = models.CharField(max_length=100, blank=True)
  exchange = models.CharField(max_length=50, blank=True)
  currency = models.CharField(max_length=10, default="USD")
  is_active = models.BooleanField(default=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    ordering = ["symbol"]

  def save(self, *args, **kwargs):
    self.symbol = self.symbol.strip().upper()
    self.currency = self.currency.strip().upper() or "USD"
    super().save(*args, **kwargs)

  def __str__(self) -> str:
    return f"{self.symbol} - {self.name}"


class StockPrice(models.Model):
  stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name="prices")
  date = models.DateField()
  open = models.DecimalField(max_digits=14, decimal_places=4)
  high = models.DecimalField(max_digits=14, decimal_places=4)
  low = models.DecimalField(max_digits=14, decimal_places=4)
  close = models.DecimalField(max_digits=14, decimal_places=4)
  adjusted_close = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
  volume = models.BigIntegerField()
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    constraints = [
        models.UniqueConstraint(fields=["stock", "date"], name="market_stock_price_stock_date_unique"),
    ]
    indexes = [
        models.Index(fields=["stock", "date"], name="stock_price_stock_date_idx"),
    ]
    ordering = ["stock__symbol", "date"]

  def __str__(self) -> str:
    return f"{self.stock.symbol} {self.date}"
