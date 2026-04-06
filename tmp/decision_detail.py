from typing import Any, Dict

from apps.emailing.models import InboundDecision, InboundEmail
from apps.updates.models import RuleEvaluationLog
from apps.updates.decision_output import build_decision_output


def _is_valid_decision_output(decision_output: Dict[str, Any]) -> bool:
    """
    Determina si un decision_output contiene una decisión real.

    Regla:
    - explanation NO cuenta
    - debe existir al menos:
        - selected_rules
        - discarded_rules
        - final_effect
    """
    if not isinstance(decision_output, dict):
        return False

    return bool(
        decision_output.get("selected_rules")
        or decision_output.get("discarded_rules")
        or decision_output.get("final_effect")
    )


def _extract_trace(email_id: int):
    """
    Recupera el trace más reciente para el email.
    """
    log = (
        RuleEvaluationLog.objects.filter(
            source_type="inbound_email",
            source_id=str(email_id),
        )
        .order_by("-created_at")
        .first()
    )

    if not log:
        return None

    return log.trace


def _extract_decision_output(trace):
    """
    Construye decision_output desde trace si existe.
    """
    if not trace:
        return None

    try:
        return build_decision_output(trace)
    except Exception:
        return None


def _extract_operational_decision(email_id: int):
    """
    Recupera decisión operativa persistida.
    """
    try:
        return InboundDecision.objects.get(email_id=email_id)
    except InboundDecision.DoesNotExist:
        return None


def _normalize_context(
    email,
    decision_output,
    operational_decision,
):
    """
    Normaliza contexto para template.
    """
    has_decision_output = _is_valid_decision_output(decision_output)
    has_operational_decision = operational_decision is not None

    if has_decision_output:
        state = "decision"
    elif has_operational_decision:
        state = "operational"
    else:
        state = "empty"

    return {
        "email": email,
        "state": state,
        "decision_output": decision_output if has_decision_output else None,
        "operational_decision": operational_decision,
    }


def get_email_decision_view(email_id: int):
    """
    Entry point para Decision Detail View.
    """
    email = InboundEmail.objects.get(id=email_id)

    trace = _extract_trace(email_id)
    decision_output = _extract_decision_output(trace)
    operational_decision = _extract_operational_decision(email_id)

    context = _normalize_context(
        email=email,
        decision_output=decision_output,
        operational_decision=operational_decision,
    )

    return context
