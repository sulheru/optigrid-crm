# Generated manually for Simulated Persona V1

import django.core.validators
import django.db.models.deletion
from decimal import Decimal
from django.db import migrations, models


SCALE_VALIDATORS = [
    django.core.validators.MinValueValidator(Decimal("0.00")),
    django.core.validators.MaxValueValidator(Decimal("1.00")),
]


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("tenancy", "0002_seed_default_orgs"),
    ]

    operations = [
        migrations.CreateModel(
            name="SimulatedPersona",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("slug", models.SlugField(help_text="Stable identifier for prompt/runtime lookup inside the simulated tenant.", max_length=120)),
                ("full_name", models.CharField(max_length=255)),
                ("first_name", models.CharField(blank=True, max_length=120)),
                ("last_name", models.CharField(blank=True, max_length=120)),
                ("job_title", models.CharField(blank=True, max_length=255)),
                ("simulated_company_name", models.CharField(blank=True, max_length=255)),
                ("seniority", models.CharField(choices=[("intern", "Intern"), ("junior", "Junior"), ("mid", "Mid"), ("senior", "Senior"), ("lead", "Lead"), ("director", "Director"), ("vp", "VP"), ("c_level", "C-Level"), ("owner", "Owner")], default="mid", max_length=32)),
                ("notes", models.TextField(blank=True)),
                ("character_seed", models.TextField(blank=True, help_text="Internal short seed describing the persona core.")),
                ("formality", models.DecimalField(decimal_places=2, default=Decimal("0.50"), max_digits=4, validators=SCALE_VALIDATORS)),
                ("patience", models.DecimalField(decimal_places=2, default=Decimal("0.50"), max_digits=4, validators=SCALE_VALIDATORS)),
                ("risk_tolerance", models.DecimalField(decimal_places=2, default=Decimal("0.50"), max_digits=4, validators=SCALE_VALIDATORS)),
                ("change_openness", models.DecimalField(decimal_places=2, default=Decimal("0.50"), max_digits=4, validators=SCALE_VALIDATORS)),
                ("cooperation", models.DecimalField(decimal_places=2, default=Decimal("0.50"), max_digits=4, validators=SCALE_VALIDATORS)),
                ("resistance", models.DecimalField(decimal_places=2, default=Decimal("0.50"), max_digits=4, validators=SCALE_VALIDATORS)),
                ("responsiveness", models.DecimalField(decimal_places=2, default=Decimal("0.50"), max_digits=4, validators=SCALE_VALIDATORS)),
                ("detail_orientation", models.DecimalField(decimal_places=2, default=Decimal("0.50"), max_digits=4, validators=SCALE_VALIDATORS)),
                ("communication_style", models.CharField(choices=[("concise", "Concise"), ("balanced", "Balanced"), ("explanatory", "Explanatory"), ("relational", "Relational"), ("direct", "Direct")], default="balanced", max_length=32)),
                ("preferred_language", models.CharField(default="en", max_length=32)),
                ("typical_reply_latency_hours", models.PositiveIntegerField(default=24)),
                ("goals", models.JSONField(blank=True, default=list)),
                ("pains", models.JSONField(blank=True, default=list)),
                ("priorities", models.JSONField(blank=True, default=list)),
                ("internal_pressures", models.JSONField(blank=True, default=list)),
                ("budget_context", models.TextField(blank=True)),
                ("decision_frame", models.CharField(choices=[("individual", "Individual"), ("manager_review", "Manager Review"), ("committee", "Committee"), ("procurement", "Procurement"), ("exec_sponsor", "Executive Sponsor"), ("unknown", "Unknown")], default="unknown", max_length=32)),
                ("decision_criteria", models.JSONField(blank=True, default=list)),
                ("blockers", models.JSONField(blank=True, default=list)),
                ("interest_level", models.DecimalField(decimal_places=2, default=Decimal("0.30"), max_digits=4, validators=SCALE_VALIDATORS)),
                ("trust_level", models.DecimalField(decimal_places=2, default=Decimal("0.30"), max_digits=4, validators=SCALE_VALIDATORS)),
                ("saturation_level", models.DecimalField(decimal_places=2, default=Decimal("0.10"), max_digits=4, validators=SCALE_VALIDATORS)),
                ("urgency_level", models.DecimalField(decimal_places=2, default=Decimal("0.20"), max_digits=4, validators=SCALE_VALIDATORS)),
                ("frustration_level", models.DecimalField(decimal_places=2, default=Decimal("0.10"), max_digits=4, validators=SCALE_VALIDATORS)),
                ("relational_temperature", models.CharField(choices=[("cold", "Cold"), ("guarded", "Guarded"), ("neutral", "Neutral"), ("warm", "Warm"), ("engaged", "Engaged"), ("friction", "Friction")], default="neutral", max_length=32)),
                ("last_interaction_at", models.DateTimeField(blank=True, null=True)),
                ("state_last_updated_at", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("mailbox_account", models.ForeignKey(blank=True, help_text="Mailbox actor primarily associated with this simulated persona.", null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="simulated_personas", to="tenancy.mailboxaccount")),
                ("operating_organization", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="simulated_personas", to="tenancy.operatingorganization")),
            ],
            options={
                "ordering": ["full_name", "id"],
                "unique_together": {("operating_organization", "slug")},
            },
        ),
        migrations.CreateModel(
            name="SimulatedPersonaMemory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("kind", models.CharField(choices=[("general", "General"), ("relation", "Relation"), ("sales", "Sales"), ("objection", "Objection"), ("internal", "Internal")], default="general", max_length=32)),
                ("title", models.CharField(max_length=255)),
                ("content", models.TextField()),
                ("salience", models.DecimalField(decimal_places=2, default=Decimal("0.50"), max_digits=4, validators=SCALE_VALIDATORS)),
                ("source", models.CharField(default="manual", max_length=64)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("persona", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="memories", to="simulated_personas.simulatedpersona")),
            ],
            options={
                "ordering": ["-salience", "-updated_at", "-id"],
            },
        ),
        migrations.AddIndex(
            model_name="simulatedpersona",
            index=models.Index(fields=["operating_organization", "is_active"], name="sim_persona_org_active_idx"),
        ),
        migrations.AddIndex(
            model_name="simulatedpersona",
            index=models.Index(fields=["operating_organization", "mailbox_account"], name="sim_persona_org_mailbox_idx"),
        ),
        migrations.AddIndex(
            model_name="simulatedpersona",
            index=models.Index(fields=["operating_organization", "slug"], name="sim_persona_org_slug_idx"),
        ),
        migrations.AddIndex(
            model_name="simulatedpersona",
            index=models.Index(fields=["relational_temperature", "is_active"], name="sim_persona_temp_active_idx"),
        ),
        migrations.AddIndex(
            model_name="simulatedpersonamemory",
            index=models.Index(fields=["persona", "kind", "is_active"], name="sim_memory_persona_kind_idx"),
        ),
        migrations.AddIndex(
            model_name="simulatedpersonamemory",
            index=models.Index(fields=["persona", "salience"], name="sim_memory_persona_salience_idx"),
        ),
    ]
