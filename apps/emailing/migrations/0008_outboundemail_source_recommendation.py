# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/emailing/migrations/0008_outboundemail_source_recommendation.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("recommendations", "0002_alter_airecommendation_status"),
        ("emailing", "0007_inboundinterpretation_inbounddecision"),
    ]

    operations = [
        migrations.AddField(
            model_name="outboundemail",
            name="source_recommendation",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="generated_outbound_emails",
                to="recommendations.airecommendation",
            ),
        ),
    ]
