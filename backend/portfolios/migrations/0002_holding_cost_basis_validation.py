# Generated manually for portfolio position cost basis support.

import django.core.validators
from django.db import migrations, models


def mark_existing_price_sources(apps, schema_editor):
  portfolio_holding = apps.get_model("portfolios", "PortfolioHolding")
  portfolio_holding.objects.filter(average_cost__isnull=False).update(price_source="manual")


class Migration(migrations.Migration):

    dependencies = [
        ("portfolios", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="portfolioholding",
            name="price_source",
            field=models.CharField(
                choices=[
                    ("market_close", "Market close"),
                    ("previous_close", "Previous close"),
                    ("manual", "Manual"),
                    ("unknown", "Unknown"),
                ],
                default="unknown",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="portfolioholding",
            name="purchase_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="portfolioholding",
            name="price_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.RunPython(mark_existing_price_sources, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="portfolio",
            name="cash",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=14,
                validators=[django.core.validators.MinValueValidator(0)],
            ),
        ),
        migrations.AlterField(
            model_name="portfolioholding",
            name="average_cost",
            field=models.DecimalField(
                blank=True,
                decimal_places=6,
                max_digits=18,
                null=True,
                validators=[django.core.validators.MinValueValidator(0)],
            ),
        ),
        migrations.AlterField(
            model_name="portfolioholding",
            name="quantity",
            field=models.DecimalField(
                blank=True,
                decimal_places=8,
                max_digits=20,
                null=True,
                validators=[django.core.validators.MinValueValidator(0)],
            ),
        ),
        migrations.AddConstraint(
            model_name="portfolio",
            constraint=models.CheckConstraint(
                condition=models.Q(cash__gte=0),
                name="portfolio_cash_non_negative",
            ),
        ),
        migrations.AddConstraint(
            model_name="portfolioholding",
            constraint=models.CheckConstraint(
                condition=models.Q(quantity__isnull=True) | models.Q(quantity__gte=0),
                name="pf_hold_quantity_non_negative",
            ),
        ),
        migrations.AddConstraint(
            model_name="portfolioholding",
            constraint=models.CheckConstraint(
                condition=models.Q(average_cost__isnull=True) | models.Q(average_cost__gte=0),
                name="pf_hold_average_cost_non_negative",
            ),
        ),
        migrations.AddConstraint(
            model_name="portfolioholding",
            constraint=models.CheckConstraint(
                condition=models.Q(price_date__isnull=True)
                | (
                    models.Q(purchase_date__isnull=False)
                    & models.Q(price_date__lte=models.F("purchase_date"))
                ),
                name="pf_hold_price_date_not_after_purchase",
            ),
        ),
    ]
