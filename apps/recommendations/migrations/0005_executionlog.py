from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("recommendations", "0004_airecommendation_tenant_scope"),
    ]

    operations = [
        migrations.CreateModel(
            name="ExecutionLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("action_type", models.CharField(max_length=64)),
                ("request_payload", models.JSONField(blank=True, default=dict)),
                ("result_payload", models.JSONField(blank=True, default=dict)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("started", "Started"),
                            ("completed", "Completed"),
                            ("failed", "Failed"),
                            ("blocked", "Blocked"),
                        ],
                        default="started",
                        max_length=16,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "recommendation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="execution_logs",
                        to="recommendations.airecommendation",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at", "-id"],
            },
        ),
        migrations.AddIndex(
            model_name="executionlog",
            index=models.Index(fields=["recommendation", "status"], name="reco_execlog_status_idx"),
        ),
        migrations.AddConstraint(
            model_name="executionlog",
            constraint=models.UniqueConstraint(
                fields=("recommendation", "action_type"),
                name="uniq_executionlog_recommendation_action",
            ),
        ),
    ]
