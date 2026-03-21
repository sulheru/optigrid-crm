# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/emailing/services/inbound_analysis_service.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
from apps.emailing.models import InboundDecision, InboundInterpretation
from apps.emailing.services.decision_automation import (
    maybe_auto_apply_decision,
    score_inbound_decision,
)
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
    score, priority, risk_flags = score_inbound_decision(
        interpretation_result,
        decision_result,
    )

    decision = (
        InboundDecision.objects.filter(
            inbound_email=inbound_email,
            action_type=decision_result.action_type,
        )
        .order_by("-created_at")
        .first()
    )

    if decision:
        decision.interpretation = interpretation
        decision.payload_json = decision_result.payload
        decision.summary = decision_result.summary
        decision.requires_approval = decision_result.requires_approval
        decision.score = score
        decision.priority = priority
        decision.risk_flags = risk_flags
        decision.save(
            update_fields=[
                "interpretation",
                "payload_json",
                "summary",
                "requires_approval",
                "score",
                "priority",
                "risk_flags",
            ]
        )
        created = False
    else:
        decision = InboundDecision.objects.create(
            inbound_email=inbound_email,
            interpretation=interpretation,
            action_type=decision_result.action_type,
            status=InboundDecision.STATUS_SUGGESTED,
            payload_json=decision_result.payload,
            summary=decision_result.summary,
            requires_approval=decision_result.requires_approval,
            score=score,
            priority=priority,
            risk_flags=risk_flags,
        )
        created = True

    auto_apply_result = None
    if decision.status == InboundDecision.STATUS_SUGGESTED:
        auto_apply_result = maybe_auto_apply_decision(decision)
        decision.refresh_from_db()

    return {
        "interpretation": interpretation_to_dict(interpretation_result),
        "decision": decision_to_dict(decision_result),
        "interpretation_id": interpretation.id,
        "decision_id": decision.id,
        "decision_status": decision.status,
        "decision_created": created,
        "auto_apply_result": auto_apply_result,
    }
