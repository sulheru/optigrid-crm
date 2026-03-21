# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/services/email_ingest.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
from __future__ import annotations

from typing import Any

from services.fact_extraction import create_facts_from_email
from services.inference_engine import create_inferences_from_fact
from services.update_proposals import create_update_proposal_from_inference

try:
    from apps.recommendations.services import create_recommendation_from_inference
except Exception:
    def create_recommendation_from_inference(inference):
        return None


def process_email_message(email_message: Any) -> dict[str, Any]:
    """
    Pipeline real mínimo:

    EmailMessage
      -> FactRecord
      -> InferenceRecord
      -> CRMUpdateProposal
      -> AIRecommendation
    """
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
        "facts": facts,
        "inferences": inferences,
        "proposals": proposals,
        "recommendations": recommendations,
    }
