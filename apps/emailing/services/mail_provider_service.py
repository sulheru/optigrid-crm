from __future__ import annotations

from typing import Any

from apps.providers.mail_provider import DraftEnvelope
from apps.providers.mail_registry_v2 import get_mail_provider_by_key
from apps.providers.mail_runtime import resolve_mail_account, resolve_mail_account_ref
from apps.tenancy.models import MailboxAccount


def prepare_provider_draft(
    *,
    subject: str,
    body_text: str,
    to: list[str],
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
    reply_to_message_id: str | None = None,
    thread_ref: str | None = None,
    account_key: str | None = None,
    mailbox_account: MailboxAccount | int | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if mailbox_account is not None:
        account = resolve_mail_account_ref(mailbox_account)
    else:
        account = resolve_mail_account(account_key)

    provider = get_mail_provider_by_key(account.provider)

    result = provider.create_draft(
        account=account,
        envelope=DraftEnvelope(
            subject=subject,
            body_text=body_text,
            to=to,
            cc=cc or [],
            bcc=bcc or [],
            reply_to_message_id=reply_to_message_id,
            thread_ref=thread_ref,
            metadata=metadata or {},
        ),
    )

    return {
        "provider": result.provider,
        "account_key": result.account_key,
        "external_draft_id": result.external_draft_id,
        "provider_status": result.status,
        "provider_payload": result.payload,
    }
