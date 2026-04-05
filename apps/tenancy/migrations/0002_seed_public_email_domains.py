from django.db import migrations


PUBLIC_DOMAINS = [
    "gmail.com",
    "googlemail.com",
    "outlook.com",
    "hotmail.com",
    "live.com",
    "msn.com",
    "yahoo.com",
    "ymail.com",
    "icloud.com",
    "me.com",
    "proton.me",
    "protonmail.com",
    "aol.com",
]


def seed_public_domains(apps, schema_editor):
    PublicEmailDomain = apps.get_model("tenancy", "PublicEmailDomain")
    for domain in PUBLIC_DOMAINS:
        PublicEmailDomain.objects.get_or_create(
            domain=domain,
            defaults={
                "is_active": True,
                "notes": "Seeded by tenancy migration 0002.",
            },
        )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("tenancy", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_public_domains, noop),
    ]
