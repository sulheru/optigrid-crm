from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Optional

from apps.emailing.models import InboundDecision
from apps.emailing.services.decision_automation import (
    maybe_auto_apply_decision,
    score_inbound_decision,
)
from apps.updates.decision_output import build_decision_output


PROPOSAL_TO_ACTION_TYPE = {
    "advance_opportunity": InboundDecision.ACTION_ADVANCE_OPPORTUNITY,
    "mark_lost": InboundDecision.ACTION_MARK_LOST,
    "schedule_followup": InboundDecision.ACTION_SCHEDULE_FOLLOWUP,
    "send_information": InboundDecision.ACTION_SEND_INFORMATION,
    "send_clarification": InboundDecision.ACTION_SEND_CLARIFICATION,
    "prepare_pricing_response": InboundDecision.ACTION_SEND_INFORMATION,
    "prepare_information_response": InboundDecision.ACTION_SEND_INFORMATION,
    "prepare_clarification_response": InboundDecision.ACTION_SEND_CLARIFICATION,
    "reply_strategy": InboundDecision.ACTION_SEND_INFORMATION,
    "followup": InboundDecision.ACTION_SCHEDULE_FOLLOWUP,
    "review_manually": InboundDecision.ACTION_SEND_CLARIFICATION,
}


def _get_interpretation_for_email(inbound_email) -> Optional[Any]:
    return getattr(inbound_email, "ai_interpretation", None)


def _coerce_action_type(candidate: Any) -> Optional[str]:
    if not candidate or not isinstance(candidate, str):
        return None

    if candidate in dict(InboundDecision.ACTION_CHOICES):
        return candidate

    return PROPOSAL_TO_ACTION_TYPE.get(candidate)


def _extract_from_semantic_effect(decision_output: dict[str, Any]) -> Optional[str]:
    final_effect = decision_output.get("final_effect")

    if not isinstance(final_effect, dict):
        return None

    semantic_effect = final_effect.get("semantic_effect")
    if not isinstance(semantic_effect, dict):
        return None

    proposal_type = semantic_effect.get("proposal_type")
    return _coerce_action_type(proposal_type)


def _extract_action_type_from_final_effect(final_effect: Any) -> Optional[str]:
    if not isinstance(final_effect, dict):
        return None

    direct_candidates = (
        final_effect.get("action_type"),
        final_effect.get("proposal_type"),
        final_effect.get("effect_type"),
    )
    for candidate in direct_candidates:
        action_type = _coerce_action_type(candidate)
        if action_type:
            return action_type

    payload = final_effect.get("payload")
    if isinstance(payload, dict):
        nested_candidates = (
            payload.get("action_type"),
            payload.get("proposal_type"),
            payload.get("effect_type"),
            payload.get("template_key"),
        )
        for candidate in nested_candidates:
            action_type = _coerce_action_type(candidate)
            if action_type:
                return action_type

    semantic_effect = final_effect.get("semantic_effect")
    if isinstance(semantic_effect, dict):
        semantic_candidates = (
            semantic_effect.get("action_type"),
            semantic_effect.get("proposal_type"),
            semantic_effect.get("effect_type"),
        )
        for candidate in semantic_candidates:
            action_type = _coerce_action_type(candidate)
            if action_type:
                return action_type

        semantic_payload = semantic_effect.get("payload")
        if isinstance(semantic_payload, dict):
            nested_semantic_candidates = (
                semantic_payload.get("action_type"),
                semantic_payload.get("proposal_type"),
                semantic_payload.get("effect_type"),
                semantic_payload.get("template_key"),
            )
            for candidate in nested_semantic_candidates:
                action_type = _coerce_action_type(candidate)
                if action_type:
                    return action_type

    return None


def _extract_action_type_from_selected_rules(selected_rules: list[dict[str, Any]]) -> Optional[str]:
    for item in selected_rules:
        if not isinstance(item, dict):
            continue

        rule_name = item.get("rule")
        action_type = _coerce_action_type(rule_name)
        if action_type:
            return action_type

    return None


def _determine_action_type(decision_output: dict[str, Any], interpretation: Any) -> str:
    action_type = _extract_from_semantic_effect(decision_output)
    if action_type:
        return action_type

    final_effect = decision_output.get("final_effect")
    selected_rules = decision_output.get("selected_rules", [])

    action_type = _extract_action_type_from_final_effect(final_effect)
    if action_type:
        return action_type

    action_type = _extract_action_type_from_selected_rules(selected_rules)
    if action_type:
        return action_type

    interpreted_action = getattr(interpretation, "recommended_action", None)
    coerced = _coerce_action_type(interpreted_action)
    if coerced:
        return coerced

    return InboundDecision.ACTION_SEND_CLARIFICATION


def _build_summary(action_type: str, decision_output: dict[str, Any]) -> str:
    selected_rules = decision_output.get("selected_rules", [])
    rule_names = [
        item.get("rule")
        for item in selected_rules
        if isinstance(item, dict) and item.get("rule")
    ]

    base_summaries = {
        InboundDecision.ACTION_ADVANCE_OPPORTUNITY: "Advance opportunity based on rule-engine decision.",
        InboundDecision.ACTION_SEND_INFORMATION: "Send information based on rule-engine decision.",
        InboundDecision.ACTION_SCHEDULE_FOLLOWUP: "Schedule follow-up based on rule-engine decision.",
        InboundDecision.ACTION_MARK_LOST: "Mark opportunity as lost based on rule-engine decision.",
        InboundDecision.ACTION_SEND_CLARIFICATION: "Send clarification based on rule-engine decision.",
    }

    summary = base_summaries.get(
        action_type,
        "Apply inbound decision derived from rule-engine trace.",
    )

    if rule_names:
        return f"{summary} Selected rules: {', '.join(rule_names)}."

    return summary


def _build_payload_json(
    inbound_email,
    interpretation,
    trace: list[dict[str, Any]],
    decision_output: dict[str, Any],
) -> dict[str, Any]:
    return {
        "source": "crm_update_rule_engine",
        "source_type": "inbound_email",
        "source_id": inbound_email.id,
        "trace": trace,
        "decision_output": decision_output,
        "interpretation_snapshot": {
            "id": getattr(interpretation, "id", None),
            "intent": getattr(interpretation, "intent", None),
            "urgency": getattr(interpretation, "urgency", None),
            "sentiment": getattr(interpretation, "sentiment", None),
            "recommended_action": getattr(interpretation, "recommended_action", None),
            "confidence": float(getattr(interpretation, "confidence", 0.0) or 0.0),
        },
    }


def upsert_inbound_decision_from_trace(inbound_email, trace: list[dict[str, Any]]) -> Optional[InboundDecision]:
    if not inbound_email or not trace:
        return None

    interpretation = _get_interpretation_for_email(inbound_email)
    if interpretation is None:
        return None

    decision_output = build_decision_output(trace)
    action_type = _determine_action_type(decision_output, interpretation)
    requires_approval = action_type in {
        InboundDecision.ACTION_ADVANCE_OPPORTUNITY,
        InboundDecision.ACTION_MARK_LOST,
    }
    summary = _build_summary(action_type, decision_output)

    scoring_input = SimpleNamespace(
        action_type=action_type,
        requires_approval=requires_approval,
    )
    score, priority, risk_flags = score_inbound_decision(
        interpretation,
        scoring_input,
    )

    payload_json = _build_payload_json(
        inbound_email=inbound_email,
        interpretation=interpretation,
        trace=trace,
        decision_output=decision_output,
    )

    decision = (
        InboundDecision.objects
        .filter(inbound_email=inbound_email, interpretation=interpretation)
        .order_by("-created_at")
        .first()
    )

    if decision is None:
        decision = InboundDecision.objects.create(
            inbound_email=inbound_email,
            interpretation=interpretation,
            action_type=action_type,
            status=InboundDecision.STATUS_SUGGESTED,
            summary=summary,
            payload_json=payload_json,
            requires_approval=requires_approval,
            score=score,
            priority=priority,
            risk_flags=risk_flags,
        )
    else:
        decision.action_type = action_type
        decision.summary = summary
        decision.payload_json = payload_json
        decision.requires_approval = requires_approval
        decision.score = score
        decision.priority = priority
        decision.risk_flags = risk_flags
        decision.save(
            update_fields=[
                "action_type",
                "summary",
                "payload_json",
                "requires_approval",
                "score",
                "priority",
                "risk_flags",
            ]
        )

    if decision.status == InboundDecision.STATUS_SUGGESTED:
        maybe_auto_apply_decision(decision)

    return decision
