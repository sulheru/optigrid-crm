from __future__ import annotations

from apps.emailing.services.provider_router import process_email_with_provider
from apps.tenancy.services.eil_context import ensure_email_eil_context


def process_incoming_email(email, *, mailbox_account=None, use_provider=True):
    """
    Entry point estable del flujo inbound real.

    - Garantiza EIL antes de cualquier procesamiento.
    - Si use_provider=True, genera reply vía provider/SMLL.
    - Después continúa el pipeline CRM sobre reply y email original.
    """
    eil_context = ensure_email_eil_context(
        email,
        mailbox_account=mailbox_account,
        require_mailbox=True,
        require_address=True,
        persist=True,
    )

    reply = None

    if use_provider:
        reply = process_email_with_provider(
            email,
            mailbox_account=eil_context["mailbox_account"],
        )

        if reply is not None:
            _continue_pipeline(reply)

    _continue_pipeline(email)
    return reply


def _continue_pipeline(email):
    try:
        from apps.crm_update_engine.entrypoints import process_email
        process_email(email)
    except ModuleNotFoundError:
        print("[SMLL] CRM Update Engine no disponible, pipeline detenido aquí")
