from apps.simulated_personas.runtime.smll_engine import SimulatedIncomingMessage


def inbound_to_smll(email, *, mailbox_account):
    return SimulatedIncomingMessage(
        subject=email.subject,
        body=email.body,
        sender_email=email.from_email,
        mailbox_account_id=mailbox_account.id,
    )


def smll_to_outbound(source_email, result):
    # 🔥 IMPORT LAZY
    from apps.emailing.models import OutboundEmail

    return OutboundEmail.objects.create(
        mailbox_account_id=result.mailbox_account_id,
        opportunity=source_email.opportunity,
        to_email=source_email.from_email,
        subject=result.subject,
        body=result.reply_body,
    )
