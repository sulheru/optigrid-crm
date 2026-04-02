from typing import List, Dict, Any, Tuple

from .conditions import evaluate_condition


# =========================================================
# HELPERS (V2.4 — QUERY LAYER)
# =========================================================

def get_selected_rules(trace: List[Dict]) -> List[str]:
    return [
        entry["rule"]
        for entry in trace
        if entry.get("rule_selected") is True
    ]


def get_discarded_rules(trace: List[Dict]) -> List[Dict]:
    return [
        {
            "rule": entry.get("rule"),
            "reason": entry.get("discard_reason"),
            "event_type": entry.get("event_type"),
        }
        for entry in trace
        if entry.get("rule_discarded") is True
    ]


def get_final_effect(trace: List[Dict]) -> Dict[str, Any]:
    for entry in reversed(trace):
        if entry.get("event_type") == "final_effect":
            return entry
    return {}


# =========================================================
# CORE ENGINE
# =========================================================

def evaluate_rules(
    rules: List[Dict],
    context: Dict[str, Any],
) -> Tuple[List[Dict], List[Dict]]:
    sorted_rules = sorted(
        rules,
        key=lambda r: r.get("priority", 0),
        reverse=True,
    )

    matched_rules = []
    trace = []

    matched_proposal_types = set()
    final_matched = False

    for rule in sorted_rules:
        conditions = rule.get("conditions", [])

        # -----------------------------
        # EVALUACIÓN DE CONDICIONES
        # -----------------------------
        if not conditions:
            results = []
            is_match = True
        else:
            results = []
            for cond in conditions:
                try:
                    result = evaluate_condition(cond, context)
                except Exception:
                    result = False
                results.append(bool(result))

            is_match = all(results)

        proposal_type = rule.get("proposal", {}).get("proposal_type")
        outcome = rule.get("outcome", "normal")

        # -----------------------------
        # TRACE BASE (COMPATIBLE)
        # -----------------------------
        trace_entry = {
            "rule": rule.get("name"),
            "matched": is_match,
            "conditions": results,
            "priority": rule.get("priority"),
        }

        # -----------------------------
        # V2.2 SEMANTICS (KEEP)
        # -----------------------------
        trace_entry["condition_match"] = is_match

        # -----------------------------
        # DEFAULT EVENT TYPE
        # -----------------------------
        trace_entry["event_type"] = "rule_evaluation"

        # -----------------------------
        # HARD STOP POR FINAL
        # -----------------------------
        if final_matched:
            trace_entry["rule_discarded"] = True
            trace_entry["discard_reason"] = "shadowed_by_final_rule"
            trace_entry["event_type"] = "rule_discard_shadowed"

            trace.append(trace_entry)
            continue

        # -----------------------------
        # SKIP POR DUPLICADO
        # -----------------------------
        if is_match and proposal_type in matched_proposal_types:
            trace_entry["rule_discarded"] = True
            trace_entry["discard_reason"] = "duplicate_proposal_type"
            trace_entry["event_type"] = "rule_discard_conflict"

            trace.append(trace_entry)
            continue

        # -----------------------------
        # CONDITION NOT MATCHED
        # -----------------------------
        if not is_match:
            trace_entry["rule_discarded"] = True
            trace_entry["discard_reason"] = "condition_not_matched"
            trace_entry["event_type"] = "rule_discard_condition_failed"

        # -----------------------------
        # RULE SELECTED
        # -----------------------------
        if is_match:
            matched_rules.append(rule)
            matched_proposal_types.add(proposal_type)

            trace_entry["rule_selected"] = True
            trace_entry["selection_priority"] = rule.get("priority")
            trace_entry["is_final"] = (
                outcome == "final" or rule.get("final") is True
            )

            trace_entry["event_type"] = "rule_selection"

            if trace_entry["is_final"]:
                final_matched = True

        trace.append(trace_entry)

    # -----------------------------
    # FINAL EFFECT
    # -----------------------------
    trace.append({
        "event_type": "final_effect",
        "final_effect": True,
        "final_matched": final_matched,
        "matched_rules_count": len(matched_rules),
    })

    return matched_rules, trace
