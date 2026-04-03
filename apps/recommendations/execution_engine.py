from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from django.utils import timezone

from apps.emailing.services.mail_provider_service import prepare_provider_draft
from apps.recommendations.execution_actions import (
    RecommendationExecutionError,
    create_reply_draft_from_recommendation,
    normalized,
)
from apps.recommendations.models import AIRecommendation


@dataclass
class ExecutionRequest:
    action_type: str
    recommendation_id: int
    operating_organization_id: int
    mailbox_account_id: int
    payload: dict[str, Any] = field(default_factory=dict)
    actor: str = "system"


@dataclass
class ExecutionResult:
    executor: str
    recommendation_id: int
    action_type: str
    status: str
    operating_organization_id: int | None = None
    mailbox_account_id: int | None = None
    created_entities: dict[str, int] = field(default_factory=dict)
    updated_entities: dict[str, int | str] = field(default_factory=dict)
    side_effects: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    provider_result: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "executor": self.executor,
            "recommendation_id": self.recommendation_id,
            "action_type": self.action_type,
            "status": self.status,
            "operating_organization_id": self.operating_organization_id,
            "mailbox_account_id": self.mailbox_account_id,
            "created_entities": self.created_entities,
            "updated_entities": self.updated_entities,
            "side_effects": self.side_effects,
            "errors": self.errors,
            "provider_result": self.provider_result,
        }


def _split_recipients(raw_value: str) -> list[str]:
    if not raw_value:
        return []
    values: list[str] = []
    for part in raw_value.split(","):
        email = part.strip()
        if email:
            values.append(email)
    return values


def _mark_recommendation_executed(recommendation: AIRecommendation):
    current_status = normalized(getattr(recommendation, "status", ""))
    if current_status == "executed":
        return

    recommendation.status = AIRecommendation.STATUS_EXECUTED
    if hasattr(recommendation, "updated_at"):
        recommendation.updated_at = timezone.now()

    update_fields = ["status"]
    if hasattr(recommendation, "updated_at"):
        update_fields.append("updated_at")
    recommendation.save(update_fields=update_fields)


def build_execution_request_from_recommendation(
    recommendation: AIRecommendation,
    *,
    actor: str = "system",
) -> ExecutionRequest:
    recommendation_type = normalized(getattr(recommendation, "recommendation_type", ""))

    if recommendation_type != "reply_strategy":
        raise RecommendationExecutionError(
            f"Unsupported execution request mapping for recommendation_type='{recommendation_type}'"
        )

    if recommendation.operating_organization_id is None:
        raise RecommendationExecutionError(
            "reply_strategy requires operating_organization on AIRecommendation"
        )

    if recommendation.mailbox_account_id is None:
        raise RecommendationExecutionError(
            "reply_strategy requires mailbox_account on AIRecommendation"
        )

    return ExecutionRequest(
        action_type="prepare_reply_draft",
        recommendation_id=recommendation.id,
        operating_organization_id=recommendation.operating_organization_id,
        mailbox_account_id=recommendation.mailbox_account_id,
        payload={"recommendation_type": recommendation.recommendation_type},
        actor=actor,
    )


def execute_execution_request(
    request: ExecutionRequest,
    *,
    recommendation: AIRecommendation | None = None,
    mark_executed: bool = True,
) -> dict[str, Any]:
    if recommendation is None:
        recommendation = AIRecommendation.objects.select_related(
            "operating_organization",
            "mailbox_account",
        ).get(pk=request.recommendation_id)

    if recommendation.id != request.recommendation_id:
        raise RecommendationExecutionError("ExecutionRequest recommendation mismatch")

    if request.action_type != "prepare_reply_draft":
        raise RecommendationExecutionError(
            f"Unsupported execution action_type='{request.action_type}'"
        )

    outbound = create_reply_draft_from_recommendation(recommendation)

    outbound.operating_organization_id = request.operating_organization_id
    outbound.mailbox_account_id = request.mailbox_account_id
    outbound.save(update_fields=["operating_organization", "mailbox_account", "updated_at"])

    provider_result = prepare_provider_draft(
        subject=outbound.subject,
        body_text=outbound.body,
        to=_split_recipients(outbound.to_email),
        mailbox_account=request.mailbox_account_id,
        metadata={
            "outbound_email_id": outbound.id,
            "recommendation_id": recommendation.id,
            "execution_actor": request.actor,
        },
    )

    result = ExecutionResult(
        executor=request.actor,
        recommendation_id=recommendation.id,
        action_type=request.action_type,
        status="completed",
        operating_organization_id=request.operating_organization_id,
        mailbox_account_id=request.mailbox_account_id,
        created_entities={"outbound_email_id": outbound.id},
        updated_entities={},
        side_effects=["draft_created", "provider_draft_prepared"],
        provider_result=provider_result,
    )

    if mark_executed:
        _mark_recommendation_executed(recommendation)

    return result.to_dict()
