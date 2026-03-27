# Generated manually for PORT SYSTEM V1 foundation.
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("recommendations", "0003_airecommendation_source"),
        ("tasks", "0004_crmtask_is_revoked"),
    ]

    operations = [
        migrations.CreateModel(
            name="ExternalActionIntent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("public_id", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("intent_type", models.CharField(choices=[
                    ("email.create_draft", "Email: Create Draft"),
                    ("email.send", "Email: Send"),
                    ("calendar.create_event", "Calendar: Create Event"),
                    ("calendar.update_event", "Calendar: Update Event"),
                ], max_length=64)),
                ("port_name", models.CharField(max_length=32)),
                ("adapter_key", models.CharField(blank=True, default="", max_length=64)),
                ("provider", models.CharField(blank=True, default="", max_length=32)),
                ("target_ref_type", models.CharField(blank=True, default="", max_length=64)),
                ("target_ref_id", models.CharField(blank=True, default="", max_length=64)),
                ("source_kind", models.CharField(choices=[
                    ("recommendation", "Recommendation"),
                    ("task", "Task"),
                    ("chat", "Chat"),
                    ("workflow", "Workflow"),
                    ("system_rule", "System Rule"),
                    ("user_action", "User Action"),
                ], default="recommendation", max_length=32)),
                ("source_id", models.CharField(blank=True, default="", max_length=64)),
                ("payload", models.JSONField(blank=True, default=dict)),
                ("normalized_preview", models.JSONField(blank=True, default=dict)),
                ("policy_classification", models.CharField(choices=[
                    ("automatic", "Automatic"),
                    ("reviewable", "Reviewable"),
                    ("critical", "Critical"),
                ], default="reviewable", max_length=16)),
                ("approval_required", models.BooleanField(default=False)),
                ("approval_status", models.CharField(choices=[
                    ("not_required", "Not Required"),
                    ("pending_approval", "Pending Approval"),
                    ("approved", "Approved"),
                    ("rejected", "Rejected"),
                    ("expired", "Expired"),
                ], default="not_required", max_length=24)),
                ("dispatch_status", models.CharField(choices=[
                    ("not_dispatched", "Not Dispatched"),
                    ("ready", "Ready"),
                    ("dispatched", "Dispatched"),
                    ("acknowledged", "Acknowledged"),
                    ("completed", "Completed"),
                    ("failed", "Failed"),
                    ("cancelled", "Cancelled"),
                ], default="not_dispatched", max_length=24)),
                ("execution_status", models.CharField(choices=[
                    ("draft", "Draft"),
                    ("validated", "Validated"),
                    ("blocked", "Blocked"),
                    ("dry_run_ready", "Dry Run Ready"),
                    ("ready_to_execute", "Ready To Execute"),
                    ("executing", "Executing"),
                    ("succeeded", "Succeeded"),
                    ("failed", "Failed"),
                    ("superseded", "Superseded"),
                ], default="draft", max_length=24)),
                ("idempotency_key", models.CharField(blank=True, db_index=True, default="", max_length=255)),
                ("idempotency_scope", models.CharField(blank=True, default="provider_account", max_length=32)),
                ("risk_score", models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ("reason", models.TextField(blank=True, default="")),
                ("rationale", models.TextField(blank=True, default="")),
                ("confidence", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ("dry_run_supported", models.BooleanField(default=True)),
                ("last_error_code", models.CharField(blank=True, default="", max_length=64)),
                ("last_error_message", models.TextField(blank=True, default="")),
                ("attempt_count", models.PositiveIntegerField(default=0)),
                ("approved_at", models.DateTimeField(blank=True, null=True)),
                ("last_attempt_at", models.DateTimeField(blank=True, null=True)),
                ("dispatched_at", models.DateTimeField(blank=True, null=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("approved_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="approved_external_action_intents", to=settings.AUTH_USER_MODEL)),
                ("recommendation", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="external_action_intents", to="recommendations.airecommendation")),
                ("requested_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="requested_external_action_intents", to=settings.AUTH_USER_MODEL)),
                ("task", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="external_action_intents", to="tasks.crmtask")),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddIndex(
            model_name="externalactionintent",
            index=models.Index(fields=["intent_type"], name="external_ac_intent__f9bc7f_idx"),
        ),
        migrations.AddIndex(
            model_name="externalactionintent",
            index=models.Index(fields=["port_name"], name="external_ac_port_na_45ece4_idx"),
        ),
        migrations.AddIndex(
            model_name="externalactionintent",
            index=models.Index(fields=["provider"], name="external_ac_provider_56f7fc_idx"),
        ),
        migrations.AddIndex(
            model_name="externalactionintent",
            index=models.Index(fields=["approval_status"], name="external_ac_approval_563470_idx"),
        ),
        migrations.AddIndex(
            model_name="externalactionintent",
            index=models.Index(fields=["execution_status"], name="external_ac_executi_5046f5_idx"),
        ),
        migrations.AddIndex(
            model_name="externalactionintent",
            index=models.Index(fields=["dispatch_status"], name="external_ac_dispatch_4bfbc3_idx"),
        ),
    ]
