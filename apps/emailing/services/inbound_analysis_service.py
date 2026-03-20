from apps.emailing.models import InboundDecision, InboundInterpretation
from apps.emailing.services.inbound_decision_engine import (
    build_inbound_decision,
    decision_to_dict,
)
from apps.emailing.services.inbound_interpreter import (
    interpret_inbound_email,
    interpretation_to_dict,
)


def analyze_inbound_email(inbound_email) -> dict:
    interpretation_result = interpret_inbound_email(inbound_email)

    interpretation, _ = InboundInterpretation.objects.update_or_create(
        inbound_email=inbound_email,
        defaults={
            "intent": interpretation_result.intent,
            "urgency": interpretation_result.urgency,
            "sentiment": interpretation_result.sentiment,
            "recommended_action": interpretation_result.recommended_action,
            "confidence": interpretation_result.confidence,
            "rationale": interpretation_result.rationale,
            "signals_json": interpretation_result.signals,
        },
    )

    decision_result = build_inbound_decision(inbound_email, interpretation_result)

    decision, _ = InboundDecision.objects.update_or_create(
        inbound_email=inbound_email,
        action_type=decision_result.action_type,
        status=InboundDecision.STATUS_SUGGESTED,
        defaults={
            "interpretation": interpretation,
            "payload_json": decision_result.payload,
            "summary": decision_result.summary,
            "requires_approval": decision_result.requires_approval,
        },
    )

    return {
        "interpretation": interpretation_to_dict(interpretation_result),
        "decision": decision_to_dict(decision_result),
        "interpretation_id": interpretation.id,
        "decision_id": decision.id,
    }
