from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("tenancy", "0001_initial"),
        ("recommendations", "0003_airecommendation_source"),
    ]

    operations = [
        migrations.AddField(
            model_name="airecommendation",
            name="mailbox_account",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="recommendations", to="tenancy.mailboxaccount"),
        ),
        migrations.AddField(
            model_name="airecommendation",
            name="operating_organization",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="recommendations", to="tenancy.operatingorganization"),
        ),
    ]
