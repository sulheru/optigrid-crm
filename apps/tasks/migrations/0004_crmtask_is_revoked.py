# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/tasks/migrations/0004_crmtask_is_revoked.py
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tasks", "0003_crmtask_opportunity_crmtask_source_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="crmtask",
            name="is_revoked",
            field=models.BooleanField(default=False, db_index=True),
        ),
    ]
