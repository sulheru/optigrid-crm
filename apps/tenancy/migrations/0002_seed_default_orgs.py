from django.db import migrations


def seed_orgs(apps, schema_editor):
    OperatingOrganization = apps.get_model("tenancy", "OperatingOrganization")

    OperatingOrganization.objects.get_or_create(
        slug="optigrid-it",
        defaults={
            "name": "OptiGrid IT",
            "legal_name": "OptiGrid IT",
            "primary_domain": "optigrid-it.com",
            "is_simulated": False,
            "status": "active",
        },
    )

    OperatingOrganization.objects.get_or_create(
        slug="simlab",
        defaults={
            "name": "OptiGrid Simulation Lab",
            "legal_name": "OptiGrid Simulation Lab",
            "primary_domain": "simlab.local",
            "is_simulated": True,
            "status": "active",
        },
    )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("tenancy", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_orgs, noop),
    ]
