from apps.emailing.models import OutboundEmail
from apps.simulated_personas.runtime.smll_engine import SimulatedIncomingMessage


def inbound_to_smll(email, *, mailbox_account):
    sender_email = email.from_email or ""
    sender_name = sender_email.split("@")[0] if "@" in sender_email else sender_email

    return SimulatedIncomingMessage(
        subject=email.subject,
        body=email.body,
        sender_name=sender_name,
        sender_email=sender_email,
        thread_key=f"opportunity:{email.opportunity_id}:inbound:{email.id}",
        mailbox_account_id=mailbox_account.id,
    )


def smll_to_outbound(inbound_email, result):
    return OutboundEmail.objects.create(
        opportunity=inbound_email.opportunity,
        source_inbound=inbound_email,
        email_type=OutboundEmail.TYPE_FOLLOWUP,
        to_email=inbound_email.from_email,
        subject=result.subject,
        body=result.reply_body,
        status=OutboundEmail.STATUS_DRAFT,
        generated_by="smll",
    )
