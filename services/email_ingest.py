from __future__ import annotations

from typing import Any

from apps.tenancy.services import resolve_email_identity, resolve_organization
from services.fact_extraction import create_facts_from_email
from services.inference_engine import create_inferences_from_fact
from services.update_proposals import create_update_proposal_from_inference

try:
    from apps.recommendations.services import create_recommendation_from_inference
except Exception:
    def create_recommendation_from_inference(inference):
        return None


def _ensure_eil_context(email_message: Any) -> dict[str, Any]:
    raw_email = getattr(email_message, "from_email", None) or getattr(email_message, "to_email", None)
    resolved_identity = None
    resolved_org = getattr(email_message, "operating_organization", None)

    if raw_email:
        resolved_identity = resolve_email_identity(raw_email)

    if resolved_org is None and resolved_identity is not None:
        resolved_org = resolve_organization(resolved_identity)

    if resolved_org is not None and hasattr(email_message, "operating_organization") and getattr(email_message, "pk", None):
        if getattr(email_message, "operating_organization_id", None) is None:
            email_message.operating_organization = resolved_org
            email_message.save(update_fields=["operating_organization"])

    setattr(email_message, "_resolved_email_identity", resolved_identity)
    setattr(email_message, "_resolved_operating_organization", resolved_org)

    return {
        "email_identity": resolved_identity,
        "operating_organization": resolved_org,
    }


def process_email_message(email_message: Any) -> dict[str, Any]:
    eil_context = _ensure_eil_context(email_message)

    facts = create_facts_from_email(email_message)

    inferences = []
    for fact in facts:
        inferences.extend(create_inferences_from_fact(fact))

    proposals = []
    for inference in inferences:
        proposal = create_update_proposal_from_inference(inference)
        if proposal is not None:
            proposals.append(proposal)

    recommendations = []
    for inference in inferences:
        recommendation = create_recommendation_from_inference(inference)
        if recommendation is not None:
            recommendations.append(recommendation)

    return {
        "email_message": email_message,
        "email_identity": eil_context["email_identity"],
        "operating_organization": eil_context["operating_organization"],
        "facts": facts,
        "inferences": inferences,
        "proposals": proposals,
        "recommendations": recommendations,
    }
