from __future__ import annotations

from apps.emailing.smll_adapter import inbound_to_smll, smll_to_outbound
from apps.simulated_personas.runtime.smll_engine import build_simulated_reply
from apps.tenancy.models import MailboxAccount


def resolve_provider_mailbox(email, *, mailbox_account=None):
    if mailbox_account is not None:
        return mailbox_account

    direct_mailbox = getattr(email, "mailbox_account", None)
    if direct_mailbox is not None:
        return direct_mailbox

    mailbox_account_id = getattr(email, "mailbox_account_id", None)
    if mailbox_account_id:
        return MailboxAccount.objects.get(
            pk=mailbox_account_id,
            status=MailboxAccount.Status.ACTIVE,
        )

    raise ValueError(
        "SMLL requiere mailbox_account canónico persistido: mailbox_account explícito "
        "o email.mailbox_account presente. "
        "La resolución heurística en runtime está deshabilitada."
    )


def process_email_with_provider(email, *, mailbox_account):
    resolved_mailbox = resolve_provider_mailbox(
        email,
        mailbox_account=mailbox_account,
    )

    smll_input = inbound_to_smll(email, mailbox_account=resolved_mailbox)

    result = build_simulated_reply(
        operating_organization=resolved_mailbox.operating_organization,
        incoming_message=smll_input,
        mailbox_account=resolved_mailbox,
    )

    return smll_to_outbound(email, result)
