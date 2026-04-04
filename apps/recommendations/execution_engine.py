from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from django.conf import settings
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.emailing.services.mail_provider_service import prepare_provider_draft
from apps.recommendations.execution_actions import (
    create_reply_draft_from_recommendation,
    normalized,
)
from apps.recommendations.models import AIRecommendation, ExecutionLog


class RecommendationExecutionError(Exception):
    pass


@dataclass
class ExecutionRequest:
    action_type: str
    recommendation_id: int
    operating_organization_id: int
    mailbox_account_id: int | None
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
    execution_log_id: int | None = None
    idempotent_replay: bool = False

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
            "execution_log_id": self.execution_log_id,
            "idempotent_replay": self.idempotent_replay,
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
    update_fields = ["status"]

    if hasattr(recommendation, "updated_at"):
        recommendation.updated_at = timezone.now()
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

    return ExecutionRequest(
        action_type="prepare_reply_draft",
        recommendation_id=recommendation.id,
        operating_organization_id=recommendation.operating_organization_id,
        mailbox_account_id=recommendation.mailbox_account_id,
        payload={"recommendation_type": recommendation.recommendation_type},
        actor=actor,
    )


def _blocked_send_actions() -> set[str]:
    configured = getattr(
        settings,
        "EXECUTION_POLICY_BLOCKED_ACTIONS",
        ["send_email", "send_draft", "send_reply", "send_outbound"],
    )
    return {normalized(value) for value in configured}


def _allowed_actions() -> set[str]:
    configured = getattr(
        settings,
        "EXECUTION_POLICY_ALLOWED_ACTIONS",
        ["prepare_reply_draft"],
    )
    return {normalized(value) for value in configured}


def _request_payload(request: ExecutionRequest) -> dict[str, Any]:
    return {
        "recommendation_id": request.recommendation_id,
        "action_type": request.action_type,
        "operating_organization_id": request.operating_organization_id,
        "mailbox_account_id": request.mailbox_account_id,
        "payload": request.payload,
        "actor": request.actor,
    }


def _build_duplicate_result(
    *,
    request: ExecutionRequest,
    existing_log: ExecutionLog,
) -> dict[str, Any]:
    payload = dict(existing_log.result_payload or {})
    payload.setdefault("executor", request.actor)
    payload.setdefault("recommendation_id", request.recommendation_id)
    payload.setdefault("action_type", request.action_type)
    payload.setdefault("operating_organization_id", request.operating_organization_id)
    payload.setdefault("mailbox_account_id", request.mailbox_account_id)
    payload.setdefault("created_entities", {})
    payload.setdefault("updated_entities", {})
    payload.setdefault("errors", [])
    payload.setdefault("provider_result", {})
    side_effects = list(payload.get("side_effects") or [])
    if "execution_deduplicated" not in side_effects:
        side_effects.append("execution_deduplicated")
    payload["side_effects"] = side_effects
    payload["execution_log_id"] = existing_log.id
    payload["idempotent_replay"] = True
    return payload


def _build_blocked_result(
    *,
    request: ExecutionRequest,
    reason: str,
    execution_log_id: int | None = None,
) -> dict[str, Any]:
    return ExecutionResult(
        executor=request.actor,
        recommendation_id=request.recommendation_id,
        action_type=request.action_type,
        status=ExecutionLog.STATUS_BLOCKED,
        operating_organization_id=request.operating_organization_id,
        mailbox_account_id=request.mailbox_account_id,
        created_entities={},
        updated_entities={},
        side_effects=["execution_blocked_by_policy"],
        errors=[reason],
        provider_result={},
        execution_log_id=execution_log_id,
    ).to_dict()


def _build_failed_result(
    *,
    request: ExecutionRequest,
    error_message: str,
    execution_log_id: int | None = None,
) -> dict[str, Any]:
    return ExecutionResult(
        executor=request.actor,
        recommendation_id=request.recommendation_id,
        action_type=request.action_type,
        status=ExecutionLog.STATUS_FAILED,
        operating_organization_id=request.operating_organization_id,
        mailbox_account_id=request.mailbox_account_id,
        created_entities={},
        updated_entities={},
        side_effects=[],
        errors=[error_message],
        provider_result={},
        execution_log_id=execution_log_id,
    ).to_dict()


def _get_or_create_execution_log(
    *,
    recommendation: AIRecommendation,
    request: ExecutionRequest,
) -> tuple[ExecutionLog, bool]:
    defaults = {
        "request_payload": _request_payload(request),
        "result_payload": {},
        "status": ExecutionLog.STATUS_STARTED,
    }

    try:
        with transaction.atomic():
            execution_log, created = ExecutionLog.objects.get_or_create(
                recommendation=recommendation,
                action_type=request.action_type,
                defaults=defaults,
            )
            return execution_log, created
    except IntegrityError:
        execution_log = ExecutionLog.objects.get(
            recommendation=recommendation,
            action_type=request.action_type,
        )
        return execution_log, False


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

    execution_log, created = _get_or_create_execution_log(
        recommendation=recommendation,
        request=request,
    )
    if not created:
        return _build_duplicate_result(request=request, existing_log=execution_log)

    action_type = normalized(request.action_type)
    if action_type in _blocked_send_actions():
        blocked = _build_blocked_result(
            request=request,
            reason=f"Action '{request.action_type}' blocked by execution policy.",
            execution_log_id=execution_log.id,
        )
        execution_log.status = ExecutionLog.STATUS_BLOCKED
        execution_log.result_payload = blocked
        execution_log.save(update_fields=["status", "result_payload"])
        return blocked

    if action_type not in _allowed_actions():
        failed = _build_failed_result(
            request=request,
            error_message=f"Unsupported execution action_type='{request.action_type}'",
            execution_log_id=execution_log.id,
        )
        execution_log.status = ExecutionLog.STATUS_FAILED
        execution_log.result_payload = failed
        execution_log.save(update_fields=["status", "result_payload"])
        raise RecommendationExecutionError(failed["errors"][0])

    try:
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
            status=ExecutionLog.STATUS_COMPLETED,
            operating_organization_id=request.operating_organization_id,
            mailbox_account_id=request.mailbox_account_id,
            created_entities={"outbound_email_id": outbound.id},
            updated_entities={},
            side_effects=["draft_created", "provider_draft_prepared"],
            provider_result=provider_result,
            execution_log_id=execution_log.id,
        ).to_dict()

        if mark_executed:
            _mark_recommendation_executed(recommendation)

        execution_log.status = ExecutionLog.STATUS_COMPLETED
        execution_log.result_payload = result
        execution_log.save(update_fields=["status", "result_payload"])
        return result

    except Exception as exc:
        failed = _build_failed_result(
            request=request,
            error_message=str(exc),
            execution_log_id=execution_log.id,
        )
        execution_log.status = ExecutionLog.STATUS_FAILED
        execution_log.result_payload = failed
        execution_log.save(update_fields=["status", "result_payload"])
        return failed
