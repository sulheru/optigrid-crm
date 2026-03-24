from django.db import migrations, models


def backfill_source(apps, schema_editor):
    AIRecommendation = apps.get_model("recommendations", "AIRecommendation")
    AIRecommendation.objects.filter(source__isnull=True).update(source="rules")
    AIRecommendation.objects.filter(source="").update(source="rules")


class Migration(migrations.Migration):

    dependencies = [
        ("recommendations", "0002_alter_airecommendation_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="airecommendation",
            name="source",
            field=models.CharField(
                max_length=16,
                choices=[
                    ("rules", "Rules"),
                    ("llm", "LLM"),
                    ("merged", "Merged"),
                ],
                default="rules",
                db_index=True,
            ),
        ),
        migrations.RunPython(backfill_source, migrations.RunPython.noop),
    ]
