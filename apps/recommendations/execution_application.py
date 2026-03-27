from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.opportunities.services.promote import (
    PROMOTABLE_TASK_TYPES,
    promote_task_to_opportunity,
)
from apps.recommendations.models import AIRecommendation
from apps.recommendations.services.external_actions import ensure_external_action_intent_for_recommendation

from .execution_actions import (
    RecommendationExecutionError,
    advance_opportunity,
    create_reply_draft_from_recommendation,
    mark_opportunity_lost,
    materialize_task_from_recommendation,
    normalized,
    resolve_opportunity_for_recommendation,
)
from .execution_adapters import get_execution_adapters


@dataclass
class ExecutionResult:
    executor: str
    recommendation_id: int
    status: str
    created_entities: dict[str, int] = field(default_factory=dict)
    updated_entities: dict[str, int | str] = field(default_factory=dict)
    side_effects: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    adapters: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "executor": self.executor,
            "recommendation_id": self.recommendation_id,
            "status": self.status,
            "created_entities": self.created_entities,
            "updated_entities": self.updated_entities,
            "side_effects": self.side_effects,
            "errors": self.errors,
            "adapters": self.adapters,
        }


def _mark_recommendation_executed(recommendation: AIRecommendation):
    current_status = normalized(getattr(recommendation, "status", ""))
    if current_status == "executed":
        return

    recommendation.status = "executed"
    if hasattr(recommendation, "updated_at"):
        recommendation.updated_at = timezone.now()

    update_fields = ["status"]
    if hasattr(recommendation, "updated_at"):
        update_fields.append("updated_at")
    recommendation.save(update_fields=update_fields)


@transaction.atomic
def execute_recommendation_service(
    recommendation: AIRecommendation,
    *,
    actor: str = "system",
    mark_executed: bool = True,
) -> dict[str, Any]:
    recommendation_type = normalized(getattr(recommendation, "recommendation_type", ""))
    adapters = get_execution_adapters()

    result = ExecutionResult(
        executor=actor,
        recommendation_id=recommendation.id,
        status="completed",
        adapters={
            "mail_provider": adapters.mail_provider,
            "calendar_provider": adapters.calendar_provider,
            "llm_provider": adapters.llm_provider,
            "execution_mode": adapters.execution_mode,
        },
    )

    if recommendation_type == "reply_strategy":
        outbound = create_reply_draft_from_recommendation(recommendation)
        intent, created = ensure_external_action_intent_for_recommendation(recommendation)
        if intent is not None:
            result.side_effects.append(
                "external_intent_created" if created else "external_intent_reused"
            )
        intent, created = ensure_external_action_intent_for_recommendation(recommendation)
        if intent is not None:
            result.side_effects.append(
                "external_intent_created" if created else "external_intent_reused"
            )
        result.created_entities["outbound_email_id"] = outbound.id
        result.side_effects.append("draft_created")

    elif recommendation_type == "followup":
        task = materialize_task_from_recommendation(recommendation)
        result.created_entities["task_id"] = task.id
        result.side_effects.append("task_materialized")

    elif recommendation_type == "contact_strategy":
        task = materialize_task_from_recommendation(recommendation)
        result.created_entities["task_id"] = task.id
        result.side_effects.append("task_materialized")

    elif recommendation_type == "opportunity_review":
        task = materialize_task_from_recommendation(recommendation)
        result.created_entities["task_id"] = task.id
        result.side_effects.append("task_materialized")
        if task.task_type in PROMOTABLE_TASK_TYPES:
            opportunity = promote_task_to_opportunity(task)
            result.created_entities["opportunity_id"] = opportunity.id
            result.side_effects.append("opportunity_promoted")

    elif recommendation_type == "pricing_strategy":
        task = materialize_task_from_recommendation(recommendation)
        result.created_entities["task_id"] = task.id
        result.side_effects.append("task_materialized")

    elif recommendation_type == "advance_opportunity":
        opportunity = resolve_opportunity_for_recommendation(recommendation)
        new_stage = advance_opportunity(opportunity)
        if opportunity:
            result.updated_entities["opportunity_id"] = opportunity.id
        result.updated_entities["opportunity_stage"] = new_stage
        result.side_effects.append("opportunity_advanced")

    elif recommendation_type == "mark_lost":
        opportunity = resolve_opportunity_for_recommendation(recommendation)
        new_stage = mark_opportunity_lost(opportunity)
        if opportunity:
            result.updated_entities["opportunity_id"] = opportunity.id
        result.updated_entities["opportunity_stage"] = new_stage
        result.side_effects.append("opportunity_marked_lost")

    else:
        task = materialize_task_from_recommendation(recommendation)
        result.created_entities["task_id"] = task.id
        result.side_effects.append("task_materialized_fallback")

    if mark_executed:
        _mark_recommendation_executed(recommendation)

    return result.to_dict()
