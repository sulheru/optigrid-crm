from __future__ import annotations

from apps.emailing.smll_adapter import inbound_to_smll, smll_to_outbound
from apps.simulated_personas.runtime.smll_engine import build_simulated_reply
from apps.tenancy.services.eil_context import ensure_email_eil_context
from services.email_ingest import process_email_message


def resolve_provider_mailbox(email, *, mailbox_account=None):
    context = ensure_email_eil_context(
        email,
        mailbox_account=mailbox_account,
        require_mailbox=True,
        require_address=False,
        persist=False,
    )
    resolved_mailbox = context["mailbox_account"]
    if resolved_mailbox is None:
        raise ValueError(
            "SMLL requires canonical mailbox_account. Heuristic mailbox resolution is disabled."
        )
    return resolved_mailbox


def ensure_provider_eil_context(email, *, mailbox_account):
    return ensure_email_eil_context(
        email,
        mailbox_account=mailbox_account,
        require_mailbox=True,
        require_address=True,
        persist=True,
    )


def process_email_with_provider(email, *, mailbox_account):
    """
    Pipeline canónico para SMLL/provider-backed processing.

    Flujo:
      email -> mailbox canónico -> EIL context -> smll input ->
      simulated reply -> outbound email persistido
    """
    resolved_mailbox = resolve_provider_mailbox(
        email,
        mailbox_account=mailbox_account,
    )

    eil_context = ensure_provider_eil_context(
        email,
        mailbox_account=resolved_mailbox,
    )

    smll_input = inbound_to_smll(email, mailbox_account=resolved_mailbox)

    result = build_simulated_reply(
        operating_organization=eil_context["operating_organization"],
        incoming_message=smll_input,
        mailbox_account=resolved_mailbox,
    )

    reply = smll_to_outbound(email, result)
    setattr(reply, "_resolved_email_identity", eil_context["email_identity"])
    setattr(reply, "_resolved_operating_organization", eil_context["operating_organization"])
    setattr(reply, "_resolved_mailbox_account", resolved_mailbox)
    return reply


def route_inbound_email(email_message):
    """
    Entrada genérica para el pipeline estructural de ingestión.

    Se conserva porque otras partes del sistema pueden depender de este
    nombre como contrato estable.
    """
    return process_email_message(email_message)


__all__ = [
    "resolve_provider_mailbox",
    "ensure_provider_eil_context",
    "process_email_with_provider",
    "route_inbound_email",
]
