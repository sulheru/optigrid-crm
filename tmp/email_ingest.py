from __future__ import annotations

from typing import Any

from apps.tenancy.services.eil_context import ensure_email_eil_context
from services.fact_extraction import create_facts_from_email
from services.inference_engine import create_inferences_from_fact
from services.update_proposals import create_update_proposal_from_inference

try:
    from apps.recommendations.services import create_recommendation_from_inference
except Exception:
    def create_recommendation_from_inference(inference):
        return None


def process_email_message(email_message: Any) -> dict[str, Any]:
    eil_context = ensure_email_eil_context(
        email_message,
        require_mailbox=False,
        require_address=True,
        persist=True,
    )

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
        "mailbox_account": eil_context["mailbox_account"],
        "email_identity": eil_context["email_identity"],
        "operating_organization": eil_context["operating_organization"],
        "facts": facts,
        "inferences": inferences,
        "proposals": proposals,
        "recommendations": recommendations,
    }
