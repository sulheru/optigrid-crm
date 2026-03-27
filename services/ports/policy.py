from __future__ import annotations

from apps.external_actions.models import ExternalActionIntent
from services.ports.types import PolicyDecision


def evaluate_policy_for_intent(intent) -> PolicyDecision:
    reasons: list[str] = []

    if intent.intent_type == ExternalActionIntent.IntentType.EMAIL_SEND:
        reasons.append("HARD RULE: email.send always requires explicit human approval.")
        return PolicyDecision(
            decision="require_approval",
            classification=ExternalActionIntent.PolicyClassification.CRITICAL,
            reasons=reasons,
            requires_approval=True,
            policy_snapshot={"hard_rule": "email_send_human_approval_required"},
        )

    if intent.intent_type == ExternalActionIntent.IntentType.EMAIL_CREATE_DRAFT:
        return PolicyDecision(
            decision="allow",
            classification=ExternalActionIntent.PolicyClassification.AUTOMATIC,
            reasons=["Draft creation is allowed automatically."],
            requires_approval=False,
            policy_snapshot={"rule": "draft_creation_allowed"},
        )

    if intent.intent_type in {
        ExternalActionIntent.IntentType.CALENDAR_CREATE_EVENT,
        ExternalActionIntent.IntentType.CALENDAR_UPDATE_EVENT,
    }:
        return PolicyDecision(
            decision="require_approval",
            classification=ExternalActionIntent.PolicyClassification.REVIEWABLE,
            reasons=["Calendar actions are reviewable by default in V1."],
            requires_approval=True,
            policy_snapshot={"rule": "calendar_reviewable_default"},
        )

    return PolicyDecision(
        decision="block",
        classification=ExternalActionIntent.PolicyClassification.CRITICAL,
        reasons=[f"Unsupported intent_type: {intent.intent_type}"],
        requires_approval=False,
        policy_snapshot={"rule": "unsupported_intent_type"},
    )
