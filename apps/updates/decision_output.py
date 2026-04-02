from typing import Any, Dict, List

from .explainability import explain_trace
from .rule_engine import (
    get_discarded_rules,
    get_final_effect,
    get_selected_rules,
)


def _normalize_rules(rule_list: List[Any]) -> List[Dict[str, Any]]:
    """
    Normaliza salida de helpers a formato estructurado para UI.

    Entrada:
        ["rule_a", "rule_b"]

    Salida:
        [{"rule": "rule_a"}, {"rule": "rule_b"}]
    """
    normalized = []

    for item in rule_list:
        if isinstance(item, dict):
            normalized.append(item)
        else:
            normalized.append({"rule": item})

    return normalized


def build_decision_output(trace: List[dict]) -> Dict[str, Any]:
    """
    Construye un payload unificado listo para UI / Chat Console.

    NO:
    - reevalúa reglas
    - reparsea trace

    SÍ:
    - adapta formato para consumo externo
    """
    selected_rules_raw = get_selected_rules(trace)
    discarded_rules_raw = get_discarded_rules(trace)
    final_effect = get_final_effect(trace)
    explanation = explain_trace(trace)

    selected_rules = _normalize_rules(selected_rules_raw)
    discarded_rules = _normalize_rules(discarded_rules_raw)

    return {
        "selected_rules": selected_rules,
        "discarded_rules": discarded_rules,
        "final_effect": final_effect,
        "explanation": explanation,
    }
