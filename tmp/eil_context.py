from __future__ import annotations

from typing import Any

from apps.tenancy.models import MailboxAccount
from apps.tenancy.services.domain_resolution import resolve_email_identity, resolve_organization


def resolve_mailbox_account_for_email(
    email_obj: Any,
    *,
    mailbox_account: MailboxAccount | int | None = None,
    require_mailbox: bool = False,
) -> MailboxAccount | None:
    resolved = mailbox_account

    if isinstance(resolved, int):
        resolved = MailboxAccount.objects.select_related("operating_organization").get(
            pk=resolved
        )

    if resolved is None:
        direct_mailbox = getattr(email_obj, "mailbox_account", None)
        if direct_mailbox is not None:
            resolved = direct_mailbox

    if resolved is None:
        mailbox_account_id = getattr(email_obj, "mailbox_account_id", None)
        if mailbox_account_id:
            resolved = MailboxAccount.objects.select_related("operating_organization").get(
                pk=mailbox_account_id
            )

    if resolved is not None and resolved.status != MailboxAccount.Status.ACTIVE:
        raise ValueError(
            f"Mailbox account '{resolved.pk}' is not active for EIL resolution."
        )

    if require_mailbox and resolved is None:
        raise ValueError(
            "Canonical mailbox_account is required for this email pipeline step."
        )

    return resolved


def ensure_email_eil_context(
    email_obj: Any,
    *,
    mailbox_account: MailboxAccount | int | None = None,
    require_mailbox: bool = False,
    require_address: bool = False,
    persist: bool = True,
) -> dict[str, Any]:
    resolved_mailbox = resolve_mailbox_account_for_email(
        email_obj,
        mailbox_account=mailbox_account,
        require_mailbox=require_mailbox,
    )

    raw_email = getattr(email_obj, "from_email", None) or getattr(email_obj, "to_email", None)
    raw_email = (raw_email or "").strip()

    if require_address and not raw_email:
        raise ValueError("Email address is required for EIL resolution in this pipeline step.")

    resolved_identity = getattr(email_obj, "_resolved_email_identity", None)
    if raw_email and resolved_identity is None:
        resolved_identity = resolve_email_identity(raw_email)

    resolved_org = getattr(email_obj, "_resolved_operating_organization", None)
    if resolved_org is None:
        resolved_org = getattr(email_obj, "operating_organization", None)

    if resolved_org is None and resolved_identity is not None:
        resolved_org = resolve_organization(resolved_identity)

    if resolved_org is None and resolved_mailbox is not None:
        resolved_org = resolved_mailbox.operating_organization

    if resolved_org is None:
        raise ValueError("OperatingOrganization could not be resolved for email object.")

    if resolved_mailbox is not None:
        mailbox_org_id = resolved_mailbox.operating_organization_id
        if resolved_org.id != mailbox_org_id:
            raise ValueError(
                "Resolved operating_organization does not match mailbox_account.operating_organization."
            )

    changed_fields: list[str] = []

    if hasattr(email_obj, "mailbox_account") and resolved_mailbox is not None:
        current_mailbox_id = getattr(email_obj, "mailbox_account_id", None)
        if current_mailbox_id is None:
            setattr(email_obj, "mailbox_account", resolved_mailbox)
            changed_fields.append("mailbox_account")
        elif current_mailbox_id != resolved_mailbox.id:
            raise ValueError(
                "Email object mailbox_account does not match resolved canonical mailbox_account."
            )

    if hasattr(email_obj, "operating_organization"):
        current_org_id = getattr(email_obj, "operating_organization_id", None)
        if current_org_id is None:
            setattr(email_obj, "operating_organization", resolved_org)
            changed_fields.append("operating_organization")
        elif current_org_id != resolved_org.id:
            raise ValueError(
                "Email object operating_organization does not match resolved operating_organization."
            )

    if persist and changed_fields and getattr(email_obj, "pk", None):
        email_obj.save(update_fields=list(dict.fromkeys(changed_fields)))

    setattr(email_obj, "_resolved_mailbox_account", resolved_mailbox)
    setattr(email_obj, "_resolved_email_identity", resolved_identity)
    setattr(email_obj, "_resolved_operating_organization", resolved_org)

    return {
        "mailbox_account": resolved_mailbox,
        "email_identity": resolved_identity,
        "operating_organization": resolved_org,
    }
