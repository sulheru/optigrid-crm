from django.test import TestCase

from apps.emailing.services.smll_bootstrap import (
    create_simulated_inbound_email,
    ensure_generic_persona,
    get_default_mailbox,
)
from apps.tenancy.services.eil_context import ensure_email_eil_context
from services.email_ingest import process_email_message


class EmailEILHardeningTests(TestCase):
    def test_ensure_email_eil_context_resolves_identity_and_org(self):
        mailbox = get_default_mailbox()
        ensure_generic_persona(mailbox)

        email = create_simulated_inbound_email(
            subject="Hardening",
            body="Please send more details about pricing and scope.",
            from_email="hardening@example.com",
            mailbox_account=mailbox,
        )

        context = ensure_email_eil_context(
            email,
            mailbox_account=mailbox,
            require_mailbox=True,
            require_address=True,
            persist=True,
        )

        self.assertEqual(context["mailbox_account"].id, mailbox.id)
        self.assertEqual(context["email_identity"].email, "hardening@example.com")
        self.assertEqual(context["operating_organization"].id, mailbox.operating_organization_id)
        self.assertEqual(email.operating_organization_id, mailbox.operating_organization_id)
        self.assertEqual(email.mailbox_account_id, mailbox.id)

    def test_email_ingest_returns_resolved_eil_context(self):
        mailbox = get_default_mailbox()
        ensure_generic_persona(mailbox)

        email = create_simulated_inbound_email(
            subject="Need info",
            body="We need more information before deciding.",
            from_email="ingest-check@example.com",
            mailbox_account=mailbox,
        )

        result = process_email_message(email)

        self.assertEqual(result["mailbox_account"].id, mailbox.id)
        self.assertEqual(result["email_identity"].email, "ingest-check@example.com")
        self.assertEqual(result["operating_organization"].id, mailbox.operating_organization_id)
