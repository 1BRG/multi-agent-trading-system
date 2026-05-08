from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("conversations", "0002_alter_chatthread_stock_alter_debatesession_stock"),
        ("market", "0004_seed_supported_assets"),
    ]

    operations = [
        migrations.CreateModel(
            name="StockSignal",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "action",
                    models.CharField(
                        choices=[("BUY", "Buy"), ("SELL", "Sell"), ("HOLD", "Hold")],
                        max_length=10,
                    ),
                ),
                ("conviction", models.DecimalField(decimal_places=4, max_digits=5)),
                ("bull_thesis", models.TextField(blank=True)),
                ("bear_thesis", models.TextField(blank=True)),
                ("judge_reasoning", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "asset",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="stock_signals",
                        to="market.asset",
                    ),
                ),
                (
                    "debate_session",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="signal",
                        to="conversations.debatesession",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="stock_signals",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(
                        fields=["asset", "-created_at"],
                        name="signal_asset_date_idx",
                    ),
                ],
            },
        ),
    ]
