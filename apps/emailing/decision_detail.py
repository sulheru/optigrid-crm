from __future__ import annotations

from typing import Any, Dict, Iterable, Optional

from apps.emailing.models import InboundDecision, InboundEmail
from apps.updates.decision_output import build_decision_output
from apps.updates.models import RuleEvaluationLog


TRACE_ATTR_CANDIDATES = (
    "trace",
    "rule_trace",
    "decision_trace",
    "crm_decision_trace",
)

TRACE_CONTAINER_ATTR_CANDIDATES = (
    "payload",
    "data",
    "metadata",
)

EMAIL_TRACE_ATTR_CANDIDATES = (
    "trace",
    "rule_trace",
    "decision_trace",
    "crm_decision_trace",
    "latest_rule_trace",
)


def _first_existing_attr(obj: Any, candidates: Iterable[str]) -> Optional[Any]:
    for name in candidates:
        if hasattr(obj, name):
            return getattr(obj, name)
    return None


def _extract_trace_from_value(value: Any) -> Optional[dict]:
    if not value:
        return None

    if isinstance(value, dict):
        if "event_type" in value or "events" in value or "entries" in value:
            return value

        for key in ("trace", "rule_trace", "decision_trace"):
            nested = value.get(key)
            if isinstance(nested, dict):
                return nested

    return None


def _extract_trace_from_object(obj: Any) -> Optional[dict]:
    direct_value = _first_existing_attr(obj, TRACE_ATTR_CANDIDATES)
    direct_trace = _extract_trace_from_value(direct_value)
    if direct_trace:
        return direct_trace

    for container_name in TRACE_CONTAINER_ATTR_CANDIDATES:
        if not hasattr(obj, container_name):
            continue

        container_value = getattr(obj, container_name)
        container_trace = _extract_trace_from_value(container_value)
        if container_trace:
            return container_trace

    return None


def _get_trace_from_email(email: InboundEmail) -> Optional[dict]:
    for attr_name in EMAIL_TRACE_ATTR_CANDIDATES:
        if not hasattr(email, attr_name):
            continue

        trace = _extract_trace_from_value(getattr(email, attr_name))
        if trace:
            return trace

    return None


def _get_rule_logs_for_email(email: InboundEmail):
    return RuleEvaluationLog.objects.filter(
        source_type="inbound_email",
        source_id=str(email.id),
    ).order_by("-created_at", "-id")


def _get_trace_from_rule_logs(email: InboundEmail) -> Optional[dict]:
    for log in _get_rule_logs_for_email(email):
        trace = _extract_trace_from_object(log)
        if trace:
            return trace
    return None


def _get_latest_inbound_decision(email: InboundEmail) -> Optional[InboundDecision]:
    return (
        InboundDecision.objects
        .filter(inbound_email=email)
        .select_related("interpretation")
        .order_by("-created_at")
        .first()
    )


def _get_decision_output_from_inbound_decision(decision: Optional[InboundDecision]) -> Optional[dict]:
    if decision is None:
        return None

    payload_json = decision.payload_json or {}
    decision_output = payload_json.get("decision_output")

    if isinstance(decision_output, dict):
        return decision_output

    trace = payload_json.get("trace")
    if isinstance(trace, list) and trace:
        return build_decision_output(trace)

    return None


def _get_trace_from_inbound_decision(decision: Optional[InboundDecision]) -> Optional[dict]:
    if decision is None:
        return None

    payload_json = decision.payload_json or {}
    trace = payload_json.get("trace")

    if isinstance(trace, list) and trace:
        return trace

    return None


def _build_empty_decision_output() -> Dict[str, Any]:
    return {
        "selected_rules": [],
        "discarded_rules": [],
        "final_effect": None,
        "explanation": [
            "No decision trace is available for this email yet.",
        ],
    }


def get_email_decision_view(email_id: int) -> Dict[str, Any]:
    email = InboundEmail.objects.get(pk=email_id)

    inbound_decision = _get_latest_inbound_decision(email)
    trace = _get_trace_from_inbound_decision(inbound_decision)
    decision_output = _get_decision_output_from_inbound_decision(inbound_decision)
    trace_source = "inbound_decision" if decision_output else None

    if not decision_output:
        trace = _get_trace_from_email(email)
        if trace:
            decision_output = build_decision_output(trace)
            trace_source = "email"

    if not decision_output:
        trace = _get_trace_from_rule_logs(email)
        if trace:
            decision_output = build_decision_output(trace)
            trace_source = "rule_evaluation_log"

    if decision_output:
        has_decision = True
    else:
        decision_output = _build_empty_decision_output()
        has_decision = False
        trace_source = None

    return {
        "email": email,
        "trace": trace,
        "trace_source": trace_source,
        "has_decision": has_decision,
        "decision_output": decision_output,
        "inbound_decision": inbound_decision,
    }
