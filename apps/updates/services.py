from typing import Any

from apps.inferences.models import InferenceRecord

from .models import CRMUpdateProposal, RuleEvaluationLog
from .rule_engine import evaluate_rules
from .rules_loader import get_rules


def create_basic_proposal(
    email: Any,
    simulate: bool = False,
    rules_version: str | None = None,
):
    if email is None:
        return []

    source_type = "inbound_email"
    source_id = str(getattr(email, "id", ""))

    inferences = list(
        InferenceRecord.objects.filter(
            source_type=source_type,
            source_id=source_id,
        ).values_list("inference_type", flat=True)
    )

    context = {
        "email": email,
        "source_type": source_type,
        "source_id": source_id,
        "corporation_id": getattr(email, "corporation_id", None),
        "inferences": inferences,
    }

    rules = get_rules(context, version=rules_version)
    matched_rules, trace = evaluate_rules(rules, context)

    print("[RULE_TRACE]", trace)

    if not simulate:
        RuleEvaluationLog.objects.create(
            source_type=source_type,
            source_id=source_id,
            trace=trace,
        )

    proposals = []
    seen_proposals = set()

    for rule in matched_rules:
        proposal_data = rule["proposal"]
        proposal_type = proposal_data["proposal_type"]

        if proposal_type in seen_proposals:
            continue

        seen_proposals.add(proposal_type)

        payload = proposal_data.get("payload", {}).copy()
        payload["_meta"] = {
            "rule_name": rule.get("name"),
            "priority": rule.get("priority"),
            "rules_version": rules_version or "default",
        }

        proposal_entry = {
            "proposal_type": proposal_type,
            "payload": payload,
        }
        proposals.append(proposal_entry)

        if not simulate:
            CRMUpdateProposal.objects.get_or_create(
                source_type=source_type,
                source_id=source_id,
                proposal_type=proposal_type,
                defaults={
                    "payload": payload,
                    "status": "proposed",
                },
            )

    return proposals
