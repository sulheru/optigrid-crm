from __future__ import annotations

from apps.emailing.smll_adapter import inbound_to_smll, smll_to_outbound
from apps.simulated_personas.runtime.smll_engine import build_simulated_reply
from apps.tenancy.models import MailboxAccount
from apps.tenancy.services.domain_resolution import resolve_operating_organization_from_email


def _candidate_mailbox_addresses(email) -> list[str]:
    candidates: list[str] = []

    for attr in ("mailbox_email", "tenant_mailbox_email", "to_email"):
        value = getattr(email, attr, None)
        if isinstance(value, str) and value.strip():
            candidates.append(value.strip().lower())

    metadata = getattr(email, "metadata", None)
    if isinstance(metadata, dict):
        for key in ("mailbox_email", "tenant_mailbox_email", "to_email"):
            value = metadata.get(key)
            if isinstance(value, str) and value.strip():
                candidates.append(value.strip().lower())

    unique: list[str] = []
    seen = set()
    for value in candidates:
        if value not in seen:
            seen.add(value)
            unique.append(value)
    return unique


def resolve_provider_mailbox(email, *, mailbox_account=None):
    if mailbox_account is not None:
        return mailbox_account

    for mailbox_email in _candidate_mailbox_addresses(email):
        operating_organization = resolve_operating_organization_from_email(mailbox_email)
        if operating_organization is None:
            continue

        mailbox = (
            MailboxAccount.objects.filter(
                operating_organization=operating_organization,
                email__iexact=mailbox_email,
                status=MailboxAccount.Status.ACTIVE,
            )
            .order_by("-is_primary", "id")
            .first()
        )
        if mailbox is not None:
            return mailbox

        fallback_mailbox = (
            MailboxAccount.objects.filter(
                operating_organization=operating_organization,
                status=MailboxAccount.Status.ACTIVE,
            )
            .order_by("-is_primary", "id")
            .first()
        )
        if fallback_mailbox is not None:
            return fallback_mailbox

    raise ValueError(
        "SMLL requiere mailbox_account explícito o una dirección de mailbox "
        "resoluble del lado del sistema. "
        "InboundEmail/Opportunity aún no persisten tenant/mailbox de forma canónica."
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
