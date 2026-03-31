# Generated manually to fix wrong interactive defaults during migration.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("updates", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="crmupdateproposal",
            name="approval_required",
        ),
        migrations.RemoveField(
            model_name="crmupdateproposal",
            name="confidence",
        ),
        migrations.RemoveField(
            model_name="crmupdateproposal",
            name="proposal_status",
        ),
        migrations.RemoveField(
            model_name="crmupdateproposal",
            name="proposed_change_type",
        ),
        migrations.RemoveField(
            model_name="crmupdateproposal",
            name="proposed_payload",
        ),
        migrations.RemoveField(
            model_name="crmupdateproposal",
            name="target_entity_id",
        ),
        migrations.RemoveField(
            model_name="crmupdateproposal",
            name="target_entity_type",
        ),
        migrations.AddField(
            model_name="crmupdateproposal",
            name="payload",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="crmupdateproposal",
            name="proposal_type",
            field=models.CharField(default="legacy_migrated", max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="crmupdateproposal",
            name="source_id",
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="crmupdateproposal",
            name="source_type",
            field=models.CharField(default="legacy_backfill", max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="crmupdateproposal",
            name="status",
            field=models.CharField(default="proposed", max_length=50),
        ),
    ]
