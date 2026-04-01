from typing import List, Dict, Any, Tuple


def evaluate_rules(
    rules: List[Dict],
    context: Dict[str, Any],
) -> Tuple[List[Dict], List[Dict]]:

    sorted_rules = sorted(rules, key=lambda r: r.get("priority", 0), reverse=True)

    matched_rules = []
    trace = []

    matched_proposal_types = set()
    final_matched = False

    for rule in sorted_rules:
        conditions = rule.get("conditions", [])

        results = []
        for cond in conditions:
            try:
                results.append(cond(context))
            except Exception:
                results.append(False)

        is_match = all(results) if conditions else True

        proposal_type = rule.get("proposal", {}).get("proposal_type")
        outcome = rule.get("outcome", "normal")

        # --- si ya hay regla final → ignorar fallback
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

            if outcome == "final":
                final_matched = True

        trace.append({
            "rule": rule.get("name"),
            "matched": is_match,
            "conditions": results,
            "priority": rule.get("priority"),
        })

    return matched_rules, trace
