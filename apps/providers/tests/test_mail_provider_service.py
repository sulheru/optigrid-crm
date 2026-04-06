from types import SimpleNamespace
from unittest.mock import patch

from django.test import TestCase

from apps.emailing.services.mail_provider_service import prepare_provider_draft
from apps.tenancy.models import EmailIdentity, MailboxAccount, OperatingOrganization


class MailProviderServiceTests(TestCase):
    def test_prepare_provider_draft_returns_provider_context(self):
        result = prepare_provider_draft(
            subject="Hello",
            body_text="World",
            to=["test@example.com"],
        )
        self.assertEqual(result["provider"], "embedded")
        self.assertEqual(result["provider_status"], "draft_created")

    @patch("apps.emailing.services.mail_provider_service.get_mail_provider_by_key")
    def test_prepare_provider_draft_propagates_eil_metadata(self, mocked_get_provider):
        captured = {}

        class FakeProvider:
            def create_draft(self, *, account, envelope):
                captured["metadata"] = dict(account.metadata or {})
                captured["to"] = list(envelope.to)
                return SimpleNamespace(
                    provider=account.provider,
                    account_key=account.account_key,
                    external_draft_id="draft-1",
                    status="draft_created",
                    payload={"ok": True},
                )

        mocked_get_provider.return_value = FakeProvider()

        org = OperatingOrganization.objects.create(
            name="OptiGrid GmbH",
            slug="optigrid-gmbh-provider",
            legal_name="OptiGrid GmbH",
            primary_domain="optigrid.com",
            is_simulated=False,
            status=OperatingOrganization.Status.ACTIVE,
        )
        mailbox = MailboxAccount.objects.create(
            operating_organization=org,
            display_name="Sales",
            email="sales@optigrid.com",
            account_key="sales-main",
            provider="mail_stub",
            is_primary=True,
            status=MailboxAccount.Status.ACTIVE,
            metadata={},
        )
        identity = EmailIdentity.objects.create(
            operating_organization=org,
            email="contact@optigrid.com",
            account_key="contact@optigrid.com",
            provider="system",
            is_primary=False,
            status=EmailIdentity.Status.ACTIVE,
        )

        result = prepare_provider_draft(
            subject="Hello",
            body_text="World",
            to=["test@example.com"],
            mailbox_account=mailbox,
            email_identity=identity,
            operating_organization=org,
        )

        self.assertEqual(result["provider_status"], "draft_created")
        self.assertEqual(captured["metadata"]["mailbox_account_id"], mailbox.id)
        self.assertEqual(captured["metadata"]["operating_organization_id"], org.id)
        self.assertEqual(captured["metadata"]["email_identity_id"], identity.id)
        self.assertEqual(captured["to"], ["test@example.com"])
