# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/emailing/migrations/0008_inbounddecision_automation_fields.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("emailing", "0007_inboundinterpretation_inbounddecision"),
    ]

    operations = [
        migrations.AddField(
            model_name="inbounddecision",
            name="applied_automatically",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="inbounddecision",
            name="automation_reason",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AddField(
            model_name="inbounddecision",
            name="priority",
            field=models.CharField(
                choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")],
                default="medium",
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name="inbounddecision",
            name="risk_flags",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name="inbounddecision",
            name="score",
            field=models.FloatField(default=0.0),
        ),
    ]
