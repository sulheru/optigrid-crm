from .email_processing_patch import process_incoming_email
from .provider_router import (
    ensure_provider_eil_context,
    process_email_with_provider,
    resolve_provider_mailbox,
    route_inbound_email,
)

__all__ = [
    "process_incoming_email",
    "resolve_provider_mailbox",
    "ensure_provider_eil_context",
    "process_email_with_provider",
    "route_inbound_email",
]
