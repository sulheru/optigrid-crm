from __future__ import annotations

from apps.facts.services import create_email_fact
from apps.inferences.services import create_basic_email_inference
from apps.recommendations.services_engine import create_basic_email_recommendation
from apps.tenancy.services import resolve_email_identity, resolve_organization
from apps.updates.services import create_basic_proposal


def _ensure_eil_context(email):
    raw_email = getattr(email, "from_email", None) or getattr(email, "to_email", None)
    resolved_identity = None
    resolved_org = getattr(email, "operating_organization", None)

    if raw_email:
        resolved_identity = resolve_email_identity(raw_email)

    if resolved_org is None and resolved_identity is not None:
        resolved_org = resolve_organization(resolved_identity)

    if resolved_org is not None and hasattr(email, "operating_organization") and getattr(email, "pk", None):
        if getattr(email, "operating_organization_id", None) is None:
            email.operating_organization = resolved_org
            email.save(update_fields=["operating_organization"])

    setattr(email, "_resolved_email_identity", resolved_identity)
    setattr(email, "_resolved_operating_organization", resolved_org)

    return {
        "email_identity": resolved_identity,
        "operating_organization": resolved_org,
    }


def process_email(email):
    _ensure_eil_context(email)

    create_email_fact(email)
    create_basic_email_inference(email)
    create_basic_proposal(email)
    create_basic_email_recommendation(email)
