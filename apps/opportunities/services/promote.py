from __future__ import annotations

from apps.opportunities.models import Opportunity
from apps.recommendations.models import AIRecommendation
from apps.tasks.models import CRMTask


PROMOTABLE_TASK_TYPES = {
    "opportunity_review",
    "qualification_review",
    "prepare_proposal",
    "pricing_review",
}


def _title_from_recommendation(rec: AIRecommendation) -> str:
    text = (rec.recommendation_text or "").strip()
    if text:
        return text[:255]
    return f"Opportunity from {rec.recommendation_type}"


def can_promote_task_to_opportunity(task: CRMTask) -> bool:
    if task.is_revoked:
        return False
    if task.status in {"done", "dismissed"}:
        return False
    return task.task_type in PROMOTABLE_TASK_TYPES


def promote_recommendation_to_opportunity(
    rec: AIRecommendation,
    *,
    company_name: str = "",
    stage: str = "new",
) -> Opportunity:
    existing = (
        Opportunity.objects.filter(source_recommendation=rec)
        .order_by("-created_at")
        .first()
    )
    if existing is not None:
        if rec.status != AIRecommendation.STATUS_MATERIALIZED:
            rec.status = AIRecommendation.STATUS_MATERIALIZED
            rec.save(update_fields=["status"])
        return existing

    opportunity = Opportunity.objects.create(
        source_recommendation=rec,
        title=_title_from_recommendation(rec),
        company_name=company_name,
        stage=stage,
        confidence=rec.confidence or 0.0,
        summary=rec.recommendation_text or "",
    )

    rec.status = AIRecommendation.STATUS_MATERIALIZED
    rec.save(update_fields=["status"])

    print(
        f"[FLOW] Recommendation promoted_to_opportunity "
        f"rec_id={rec.id} opportunity_id={opportunity.id}"
    )
    return opportunity


def promote_task_to_opportunity(
    task: CRMTask,
    *,
    company_name: str = "",
    stage: str = "new",
) -> Opportunity:
    existing = Opportunity.objects.filter(source_task=task).order_by("-created_at").first()
    if existing is not None:
        return existing

    opportunity = Opportunity.objects.create(
        source_task=task,
        title=task.title[:255],
        company_name=company_name,
        stage=stage,
        summary=task.description or "",
    )

    print(f"[FLOW] Task promoted_to_opportunity task_id={task.id} opportunity_id={opportunity.id}")
    return opportunity


def maybe_promote_task_to_opportunity(
    task: CRMTask,
    *,
    company_name: str = "",
    stage: str = "new",
) -> Opportunity | None:
    if not can_promote_task_to_opportunity(task):
        return None
    return promote_task_to_opportunity(task, company_name=company_name, stage=stage)


def promote_task(task: CRMTask, **kwargs) -> Opportunity | None:
    return maybe_promote_task_to_opportunity(task, **kwargs)
