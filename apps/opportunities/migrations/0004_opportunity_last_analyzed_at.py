# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/opportunities/migrations/0004_opportunity_last_analyzed_at.py
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("opportunities", "0003_opportunity_source_recommendation"),
    ]

    operations = [
        migrations.AddField(
            model_name="opportunity",
            name="last_analyzed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
