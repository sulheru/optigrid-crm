from typing import Any, Dict
from .rules import RULES
from .rule_engine import evaluate_rules


def simulate_proposals(email: Any) -> Dict:
    if email is None:
        return {}

    source_type = "inbound_email"
    source_id = str(getattr(email, "id", ""))

    rules, trace = evaluate_rules(RULES, source_type, source_id)

    proposals = []

    seen = set()

    for rule in rules:
        proposal_data = rule["proposal"]
        proposal_type = proposal_data["proposal_type"]

        if proposal_type in seen:
            continue

        seen.add(proposal_type)

        proposals.append({
            "proposal_type": proposal_type,
            "payload": proposal_data.get("payload", {}),
            "meta": {
                "rule_name": rule.get("name"),
                "priority": rule.get("priority"),
            }
        })

    return {
        "trace": trace,
        "proposals": proposals,
    }
