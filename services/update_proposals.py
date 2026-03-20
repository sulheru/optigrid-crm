# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/services/update_proposals.py
from __future__ import annotations

from typing import Any

from apps.inferences.models import InferenceRecord
from apps.updates.models import CRMUpdateProposal


def _proposal_kwargs_for_inference(inference: InferenceRecord) -> dict[str, Any] | None:
    """
    Traduce una inferencia en una propuesta de actualización CRM
    compatible con el modelo real actual.

    Como el modelo actual exige target_entity_id NOT NULL y todavía no
    estamos materializando Contact/Opportunity reales en este slice,
    anclamos la propuesta a la propia InferenceRecord que la origina.
    """
    iv = inference.inference_value or {}

    base_target = {
        "target_entity_type": "inference_record",
        "target_entity_id": inference.id,
    }

    if inference.inference_type == "contact_role_fit" and iv.get("status") == "redirected":
        return {
            **base_target,
            "proposed_change_type": "mark_contact_redirected",
            "proposed_payload": {
                "intended_target_entity_type": "contact",
                "contact_status": "redirected",
                "source_inference_id": inference.id,
                "rationale": inference.rationale,
            },
            "confidence": inference.confidence,
            "approval_required": False,
        }

    if inference.inference_type == "next_best_action" and iv.get("action") == "follow_up_later":
        return {
            **base_target,
            "proposed_change_type": "schedule_followup_window",
            "proposed_payload": {
                "intended_target_entity_type": "opportunity",
                "suggested_timing": iv.get("suggested_timing"),
                "source_inference_id": inference.id,
                "rationale": inference.rationale,
            },
            "confidence": inference.confidence,
            "approval_required": False,
        }

    if inference.inference_type == "opportunity_probability" and iv.get("status") == "emerging_signal":
        return {
            **base_target,
            "proposed_change_type": "create_or_open_opportunity",
            "proposed_payload": {
                "intended_target_entity_type": "opportunity",
                "opportunity_status": "signal_detected",
                "signal_strength": iv.get("signal_strength", "moderate"),
                "source_inference_id": inference.id,
                "rationale": inference.rationale,
            },
            "confidence": inference.confidence,
            "approval_required": True,
        }

    return None


def create_update_proposal_from_inference(
    inference: InferenceRecord,
) -> CRMUpdateProposal | None:
    payload = _proposal_kwargs_for_inference(inference)
    if not payload:
        return None

    return CRMUpdateProposal.objects.create(
        target_entity_type=payload["target_entity_type"],
        target_entity_id=payload["target_entity_id"],
        proposed_change_type=payload["proposed_change_type"],
        proposed_payload=payload["proposed_payload"],
        confidence=payload["confidence"],
        approval_required=payload["approval_required"],
        proposal_status="pending_approval" if payload["approval_required"] else "proposed",
    )
