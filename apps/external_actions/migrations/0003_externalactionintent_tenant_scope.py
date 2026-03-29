from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("tenancy", "0001_initial"),
        ("external_actions", "0002_rename_external_ac_intent__f9bc7f_idx_external_ac_intent__32184c_idx_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="externalactionintent",
            name="mailbox_account",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="external_action_intents", to="tenancy.mailboxaccount"),
        ),
        migrations.AddField(
            model_name="externalactionintent",
            name="operating_organization",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="external_action_intents", to="tenancy.operatingorganization"),
        ),
    ]
