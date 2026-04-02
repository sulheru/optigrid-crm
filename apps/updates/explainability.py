from typing import List, Dict, Any

from .rule_engine import (
    get_selected_rules,
    get_discarded_rules,
    get_final_effect,
)


def explain_trace(trace: List[Dict[str, Any]]) -> List[str]:
    """
    V2.5 — Explainability Layer

    Traduce RULE_TRACE a una explicación legible, determinista y basada
    en el trace real.

    Principios:
    - no modifica el motor
    - no reevalúa reglas
    - reutiliza helpers existentes
    - mantiene separación: motor != explicación
    """
    if not trace:
        return ["No hay decisiones registradas en el trace."]

    selected_rules = get_selected_rules(trace)
    discarded_rules = get_discarded_rules(trace)
    final_effect = get_final_effect(trace)

    trace_by_rule = {
        entry.get("rule"): entry
        for entry in trace
        if entry.get("rule")
    }

    explanation: List[str] = []

    for rule_name in selected_rules:
        entry = trace_by_rule.get(rule_name, {})
        conditions = entry.get("conditions", [])

        if not conditions:
            explanation.append(
                f"Se seleccionó la regla '{rule_name}' porque no tenía condiciones y por tanto aplicaba directamente."
            )
            continue

        explanation.append(
            f"Se seleccionó la regla '{rule_name}' porque todas sus condiciones evaluaron a verdadero."
        )

    for discarded in discarded_rules:
        rule_name = discarded.get("rule")
        reason = discarded.get("reason")
        event_type = discarded.get("event_type")

        if event_type == "rule_discard_condition_failed":
            explanation.append(
                f"Se descartó la regla '{rule_name}' porque no se cumplieron sus condiciones."
            )
        elif event_type == "rule_discard_conflict":
            explanation.append(
                f"Se descartó la regla '{rule_name}' porque entraba en conflicto con una regla ya seleccionada del mismo proposal_type."
            )
        elif event_type == "rule_discard_shadowed":
            explanation.append(
                f"Se descartó la regla '{rule_name}' porque una regla final anterior bloqueó la evaluación efectiva del resto."
            )
        elif reason:
            explanation.append(
                f"Se descartó la regla '{rule_name}' por el motivo '{reason}'."
            )
        else:
            explanation.append(
                f"Se descartó la regla '{rule_name}'."
            )

    if final_effect:
        final_matched = final_effect.get("final_matched")
        matched_rules_count = final_effect.get("matched_rules_count", 0)

        if final_matched:
            explanation.append(
                f"El efecto final indica que se alcanzó una regla final y que el motor terminó con {matched_rules_count} regla(s) seleccionada(s)."
            )
        else:
            explanation.append(
                f"El efecto final indica que no se alcanzó ninguna regla final y que el motor terminó con {matched_rules_count} regla(s) seleccionada(s)."
            )

    if not explanation:
        return ["El trace existe, pero no contiene decisiones explicables."]

    return explanation
