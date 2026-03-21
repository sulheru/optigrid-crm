# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/emailing/services/inbound_decision_engine.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class InboundDecisionResult:
    action_type: str
    payload: dict[str, Any]
    requires_approval: bool
    summary: str


def build_inbound_decision(inbound_email, interpretation) -> InboundDecisionResult:
    opportunity = getattr(inbound_email, "opportunity", None)
    opportunity_id = getattr(opportunity, "id", None)
    action = interpretation.recommended_action

    if action == "advance_opportunity":
        return InboundDecisionResult(
            action_type=action,
            requires_approval=True,
            summary="Advance opportunity to qualifying state.",
            payload={
                "opportunity_id": opportunity_id,
                "target_stage": "qualifying",
                "priority_delta": 1,
                "confidence_delta": 0.10,
                "risk_flags_to_add": [],
            },
        )

    if action == "send_information":
        return InboundDecisionResult(
            action_type=action,
            requires_approval=False,
            summary="Generate informational follow-up draft.",
            payload={
                "opportunity_id": opportunity_id,
                "draft_type": "followup",
                "template_key": "needs_info_response",
            },
        )

    if action == "schedule_followup":
        return InboundDecisionResult(
            action_type=action,
            requires_approval=False,
            summary="Create future follow-up action.",
            payload={
                "opportunity_id": opportunity_id,
                "task_type": "followup",
                "delay_days": 14,
                "target_stage": "deferred",
            },
        )

    if action == "mark_lost":
        return InboundDecisionResult(
            action_type=action,
            requires_approval=True,
            summary="Mark opportunity as lost/inactive.",
            payload={
                "opportunity_id": opportunity_id,
                "target_stage": "lost",
                "priority_delta": -2,
                "confidence_delta": -0.30,
                "risk_flags_to_add": ["explicit_rejection"],
            },
        )

    return InboundDecisionResult(
        action_type="send_clarification",
        requires_approval=False,
        summary="Generate clarification follow-up draft.",
        payload={
            "opportunity_id": opportunity_id,
            "draft_type": "followup",
            "template_key": "clarification_request",
        },
    )


def decision_to_dict(result: InboundDecisionResult) -> dict[str, Any]:
    return asdict(result)
