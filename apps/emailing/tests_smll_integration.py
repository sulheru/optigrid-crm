from django.test import TestCase

from apps.emailing.models import InboundEmail, OutboundEmail
from apps.emailing.services.email_processing_patch import process_incoming_email
from apps.emailing.services.smll_bootstrap import (
    create_simulated_inbound_email,
    ensure_generic_persona,
    get_default_mailbox,
)
from apps.opportunities.models import Opportunity


class SMLLIntegrationV1Tests(TestCase):
    def test_process_incoming_email_generates_smll_outbound(self):
        mailbox = get_default_mailbox()
        ensure_generic_persona(mailbox)

        before_inbound = InboundEmail.objects.count()
        before_outbound = OutboundEmail.objects.count()
        before_opps = Opportunity.objects.count()

        email = create_simulated_inbound_email(
            subject="Test SMLL",
            body="We are exploring improvements in our IT setup and would like to understand your approach.",
            from_email="test@company.com",
            mailbox_account=mailbox,
        )

        reply = process_incoming_email(
            email,
            mailbox_account=mailbox,
        )

        self.assertIsNotNone(reply)

        self.assertEqual(InboundEmail.objects.count(), before_inbound + 1)
        self.assertEqual(OutboundEmail.objects.count(), before_outbound + 1)
        self.assertEqual(Opportunity.objects.count(), before_opps + 1)

        self.assertEqual(
            getattr(email, "_resolved_email_identity", None).email,
            "test@company.com",
        )
        self.assertEqual(
            getattr(reply, "_resolved_email_identity", None).email,
            "test@company.com",
        )
        self.assertEqual(
            getattr(email, "_resolved_operating_organization", None).id,
            mailbox.operating_organization_id,
        )
        self.assertEqual(
            getattr(reply, "_resolved_operating_organization", None).id,
            mailbox.operating_organization_id,
        )

        reply.refresh_from_db()
        email.refresh_from_db()

        self.assertEqual(reply.opportunity_id, email.opportunity_id)
        self.assertEqual(reply.source_inbound_id, email.id)
        self.assertEqual(reply.to_email, "test@company.com")
        self.assertEqual(reply.generated_by, "smll")
        self.assertEqual(reply.status, OutboundEmail.STATUS_DRAFT)
        self.assertEqual(reply.email_type, OutboundEmail.TYPE_FOLLOWUP)
        self.assertEqual(email.operating_organization_id, mailbox.operating_organization_id)
        self.assertEqual(reply.operating_organization_id, mailbox.operating_organization_id)
        self.assertEqual(reply.mailbox_account_id, mailbox.id)
