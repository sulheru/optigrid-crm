from typing import List, Dict, Any, Tuple

from .conditions import evaluate_condition


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
        # V2.2 TRACE SEMANTICS (ADDITIVE)
        # -----------------------------
        trace_entry["condition_match"] = is_match

        # -----------------------------
        # HARD STOP POR FINAL (FIX CLAVE)
        # -----------------------------
        if final_matched:
            trace_entry["rule_discarded"] = True
            trace_entry["discard_reason"] = "shadowed_by_final_rule"

            trace.append(trace_entry)
            continue

        # -----------------------------
        # SKIP POR CONFLICTO
        # -----------------------------
        if is_match and proposal_type in matched_proposal_types:
            trace_entry["rule_discarded"] = True
            trace_entry["discard_reason"] = "duplicate_proposal_type"

            trace.append(trace_entry)
            continue

        # -----------------------------
        # CONDITION NOT MATCHED
        # -----------------------------
        if not is_match:
            trace_entry["rule_discarded"] = True
            trace_entry["discard_reason"] = "condition_not_matched"

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

            if trace_entry["is_final"]:
                final_matched = True

        trace.append(trace_entry)

    # -----------------------------
    # FINAL EFFECT (V2.2)
    # -----------------------------
    trace.append({
        "final_effect": True,
        "final_matched": final_matched,
        "matched_rules_count": len(matched_rules),
    })

    return matched_rules, trace
