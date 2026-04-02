from typing import Any, Dict, List

from apps.updates.decision_output import build_decision_output


TRACE_ATTR_CANDIDATES = (
    "rule_trace",
    "decision_trace",
    "crm_update_trace",
    "trace",
)


def resolve_email_trace(email_obj: Any) -> List[dict]:
    """
    Resuelve el RULE_TRACE desde el email sin acoplarse a un único nombre
    de atributo. Si no existe trace, devuelve lista vacía.
    """
    for attr_name in TRACE_ATTR_CANDIDATES:
        if hasattr(email_obj, attr_name):
            value = getattr(email_obj, attr_name)
            if isinstance(value, list):
                return value
    return []


def build_email_decision_context(email_obj: Any) -> Dict[str, Any]:
    trace = resolve_email_trace(email_obj)
    decision_output = build_decision_output(trace)

    return {
        "email": email_obj,
        "trace": trace,
        "decision_output": decision_output,
        "has_decision_trace": bool(trace),
    }
