from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="OperatingOrganization",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("slug", models.SlugField(blank=True, max_length=120, unique=True)),
                ("legal_name", models.CharField(blank=True, max_length=255)),
                ("primary_domain", models.CharField(blank=True, max_length=255)),
                ("is_simulated", models.BooleanField(default=False)),
                ("status", models.CharField(choices=[("active", "Active"), ("paused", "Paused"), ("archived", "Archived")], default="active", max_length=20)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="created_operating_organizations", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Operating Organization",
                "verbose_name_plural": "Operating Organizations",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="MailboxAccount",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("display_name", models.CharField(blank=True, max_length=200)),
                ("email", models.EmailField(max_length=254)),
                ("account_key", models.CharField(max_length=120)),
                ("provider", models.CharField(default="mail_stub", max_length=100)),
                ("is_primary", models.BooleanField(default=False)),
                ("status", models.CharField(choices=[("active", "Active"), ("disabled", "Disabled"), ("archived", "Archived")], default="active", max_length=20)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("operating_organization", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="mailbox_accounts", to="tenancy.operatingorganization")),
                ("owner_user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="mailbox_accounts", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Mailbox Account",
                "verbose_name_plural": "Mailbox Accounts",
                "ordering": ["operating_organization__name", "email"],
                "unique_together": {("operating_organization", "email"), ("operating_organization", "account_key")},
            },
        ),
    ]
