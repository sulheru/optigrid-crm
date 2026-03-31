from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tenancy", "0002_seed_default_orgs"),
    ]

    operations = [
        migrations.CreateModel(
            name="CorporateDomain",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("domain", models.CharField(max_length=255, unique=True)),
                ("is_primary", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "operating_organization",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="corporate_domains",
                        to="tenancy.operatingorganization",
                    ),
                ),
            ],
            options={
                "ordering": ["domain"],
            },
        ),

        migrations.CreateModel(
            name="Identity",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("display_name", models.CharField(blank=True, max_length=200)),
                ("status", models.CharField(max_length=20, default="active")),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),

        migrations.CreateModel(
            name="CorporateMembership",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("role", models.CharField(max_length=20, default="member")),
                ("status", models.CharField(max_length=20, default="active")),
                ("is_default", models.BooleanField(default=False)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "identity",
                    models.ForeignKey(on_delete=models.deletion.CASCADE, to="tenancy.identity"),
                ),
                (
                    "operating_organization",
                    models.ForeignKey(on_delete=models.deletion.CASCADE, to="tenancy.operatingorganization"),
                ),
            ],
        ),

        # ✅ NOMBRES CORTOS Y VÁLIDOS
        migrations.AddIndex(
            model_name="corporatedomain",
            index=models.Index(fields=["domain"], name="cd_dom_idx"),
        ),
        migrations.AddIndex(
            model_name="corporatedomain",
            index=models.Index(fields=["operating_organization", "is_active"], name="cd_org_act_idx"),
        ),
        migrations.AddIndex(
            model_name="corporatemembership",
            index=models.Index(fields=["operating_organization", "status"], name="cm_org_st_idx"),
        ),
        migrations.AddIndex(
            model_name="corporatemembership",
            index=models.Index(fields=["identity", "status"], name="cm_id_st_idx"),
        ),

        migrations.AddConstraint(
            model_name="corporatemembership",
            constraint=models.UniqueConstraint(
                fields=("identity", "operating_organization"),
                name="uniq_id_org",
            ),
        ),
    ]
