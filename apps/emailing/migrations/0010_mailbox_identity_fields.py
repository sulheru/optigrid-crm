from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tenancy", "0004_alter_corporatedomain_options_and_more"),
        ("emailing", "0009_merge_0008_emailing_branches"),
    ]

    operations = [
        migrations.AddField(
            model_name="inboundemail",
            name="mailbox_account",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
                related_name="inbound_emails",
                to="tenancy.mailboxaccount",
            ),
        ),
        migrations.AddField(
            model_name="inboundemail",
            name="operating_organization",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
                related_name="inbound_emails",
                to="tenancy.operatingorganization",
            ),
        ),
        migrations.AddField(
            model_name="outboundemail",
            name="mailbox_account",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
                related_name="outbound_emails",
                to="tenancy.mailboxaccount",
            ),
        ),
        migrations.AddField(
            model_name="outboundemail",
            name="operating_organization",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
                related_name="outbound_emails",
                to="tenancy.operatingorganization",
            ),
        ),
    ]
