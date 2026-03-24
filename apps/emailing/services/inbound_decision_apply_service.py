import logging

from django.db import transaction
from django.utils import timezone

from apps.emailing.models import InboundDecision
from apps.emailing.services.recommendation_bridge import ensure_recommendation_for_inbound_decision
from apps.recommendations.execution import (
    RecommendationExecutionError,
    execute_recommendation_service,
)

logger = logging.getLogger(__name__)


@transaction.atomic
def apply_inbound_decision(
    decision: InboundDecision,
    automatic: bool = False,
    automation_reason: str = "",
):
    if decision.status != InboundDecision.STATUS_SUGGESTED:
        raise ValueError("Decision is not in suggested state")

    logger.info(
        "Applying inbound decision %s for inbound %s with action %s (automatic=%s)",
        decision.id,
        decision.inbound_email_id,
        decision.action_type,
        automatic,
    )

    recommendation = ensure_recommendation_for_inbound_decision(decision)

    try:
        execution = execute_recommendation_service(
            recommendation,
            actor="inbox_intelligence_auto" if automatic else "inbox_intelligence_manual",
            mark_executed=True,
        )
    except RecommendationExecutionError:
        logger.exception("Failed to execute recommendation for inbound decision %s", decision.id)
        raise

    decision.status = InboundDecision.STATUS_APPLIED
    decision.applied_at = timezone.now()
    decision.applied_automatically = automatic

    update_fields = [
        "status",
        "applied_at",
        "applied_automatically",
    ]

    if automatic:
        decision.automation_reason = automation_reason or "auto_apply"
        update_fields.append("automation_reason")

    decision.save(update_fields=update_fields)

    return {
        "decision_id": decision.id,
        "recommendation_id": recommendation.id,
        "automatic": automatic,
        "execution": execution,
        "task_id": execution.get("created_entities", {}).get("task_id"),
        "outbound_id": execution.get("created_entities", {}).get("outbound_email_id"),
        "opportunity_stage": execution.get("updated_entities", {}).get("opportunity_stage"),
    }


def dismiss_inbound_decision(decision: InboundDecision):
    if decision.status != InboundDecision.STATUS_SUGGESTED:
        raise ValueError("Only suggested decisions can be dismissed")

    logger.info(
        "Dismissing inbound decision %s for inbound %s",
        decision.id,
        decision.inbound_email_id,
    )

    decision.status = InboundDecision.STATUS_DISMISSED
    decision.save(update_fields=["status"])

    return {"decision_id": decision.id}
