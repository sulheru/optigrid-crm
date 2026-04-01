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

        # Compatibilidad: [] => match por defecto
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

        if final_matched and outcome == "fallback":
            trace.append({
                "rule": rule.get("name"),
                "matched": False,
                "skipped_due_to_final": True,
                "priority": rule.get("priority"),
            })
            continue

        if is_match and proposal_type in matched_proposal_types:
            trace.append({
                "rule": rule.get("name"),
                "matched": False,
                "skipped_due_to_conflict": True,
                "priority": rule.get("priority"),
            })
            continue

        if is_match:
            matched_rules.append(rule)
            matched_proposal_types.add(proposal_type)

            if outcome == "final" or rule.get("final") is True:
                final_matched = True

        trace.append({
            "rule": rule.get("name"),
            "matched": is_match,
            "conditions": results,
            "priority": rule.get("priority"),
        })

    return matched_rules, trace
