from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("strategies", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="strategy",
            name="status",
            field=models.CharField(choices=[('draft', 'Draft'), ('approved', 'Approved'), ('archived', 'Archived')], default='approved', max_length=20),
        ),
        migrations.AddField(
            model_name="strategy",
            name="raw_llm_response",
            field=models.TextField(blank=True),
        ),
    ]
