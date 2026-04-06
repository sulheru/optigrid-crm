from django.test import TestCase

from apps.providers.mail_runtime import enrich_mail_account_ref, resolve_mail_account
from apps.tenancy.models import EmailIdentity, OperatingOrganization


class MailRuntimeTests(TestCase):
    def test_resolve_default_account(self):
        account = resolve_mail_account()
        self.assertEqual(account.account_key, "default")
        self.assertEqual(account.provider, "embedded")

    def test_enrich_mail_account_ref_adds_eil_metadata(self):
        org = OperatingOrganization.objects.create(
            name="OptiGrid GmbH",
            slug="optigrid-gmbh-runtime",
            legal_name="OptiGrid GmbH",
            primary_domain="optigrid.com",
            is_simulated=False,
            status=OperatingOrganization.Status.ACTIVE,
        )
        identity = EmailIdentity.objects.create(
            operating_organization=org,
            email="hello@optigrid.com",
            account_key="hello@optigrid.com",
            provider="system",
            is_primary=False,
            status=EmailIdentity.Status.ACTIVE,
        )

        account = resolve_mail_account()
        enriched = enrich_mail_account_ref(
            account,
            operating_organization=org,
            email_identity=identity,
        )

        self.assertEqual(enriched.metadata["operating_organization_id"], org.id)
        self.assertEqual(enriched.metadata["email_identity_id"], identity.id)
