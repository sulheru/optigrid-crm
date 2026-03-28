from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="KnowledgeCandidate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("candidate_type", models.CharField(choices=[("FAQ", "FAQ"), ("BEHAVIOR", "Behavior"), ("CAPABILITY_PROPOSAL", "Capability Proposal")], max_length=32)),
                ("content", models.TextField()),
                ("confidence_score", models.FloatField(default=0.0)),
                ("source_examples", models.JSONField(blank=True, default=list)),
                ("status", models.CharField(choices=[("proposed", "Proposed"), ("accepted", "Accepted"), ("rejected", "Rejected")], default="proposed", max_length=16)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("source_signature", models.CharField(blank=True, max_length=128, unique=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("reviewed_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={"ordering": ("-created_at", "-id")},
        ),
        migrations.CreateModel(
            name="VectorMemoryItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("namespace", models.CharField(default="default", max_length=64)),
                ("source_model", models.CharField(max_length=128)),
                ("source_pk", models.CharField(max_length=64)),
                ("source_text", models.TextField()),
                ("embedding", models.JSONField(blank=True, default=list)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ("-updated_at", "-id")},
        ),
        migrations.CreateModel(
            name="FAQEntry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("question", models.TextField()),
                ("answer", models.TextField(blank=True)),
                ("normalized_question", models.CharField(db_index=True, max_length=512)),
                ("is_active", models.BooleanField(default=True)),
                ("version", models.PositiveIntegerField(default=1)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("source_candidate", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="promoted_faq_entries", to="knowledge.knowledgecandidate")),
                ("supersedes", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="superseded_by", to="knowledge.faqentry")),
            ],
            options={"ordering": ("-updated_at", "-id")},
        ),
        migrations.CreateModel(
            name="BehaviorEntry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("instruction", models.TextField()),
                ("is_active", models.BooleanField(default=True)),
                ("version", models.PositiveIntegerField(default=1)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("source_candidate", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="promoted_behavior_entries", to="knowledge.knowledgecandidate")),
                ("supersedes", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="superseded_by", to="knowledge.behaviorentry")),
            ],
            options={"ordering": ("-updated_at", "-id")},
        ),
        migrations.CreateModel(
            name="CapabilityProposalEntry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField()),
                ("is_active", models.BooleanField(default=False)),
                ("version", models.PositiveIntegerField(default=1)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("source_candidate", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="promoted_capability_entries", to="knowledge.knowledgecandidate")),
                ("supersedes", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="superseded_by", to="knowledge.capabilityproposalentry")),
            ],
            options={"ordering": ("-updated_at", "-id")},
        ),
        migrations.AlterUniqueTogether(
            name="vectormemoryitem",
            unique_together={("namespace", "source_model", "source_pk")},
        ),
    ]
