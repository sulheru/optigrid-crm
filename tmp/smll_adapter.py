from __future__ import annotations

from apps.emailing.services.smll_bootstrap import get_or_create_default_mailbox


def create_simulated_inbound_email(subject: str, body: str, from_email: str):
    mailbox = get_or_create_default_mailbox()

    return {
        "subject": subject,
        "body": body,
        "from_email": from_email,
        "to_email": mailbox.email,
    }
