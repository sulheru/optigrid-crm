from __future__ import annotations

from apps.recommendations.models import AIRecommendation
from apps.tasks.models import CRMTask


TASK_TYPE_MAP = {
    "reply_email": "reply_email",
    "follow_up": "follow_up",
    "schedule_call": "schedule_call",
    "prepare_proposal": "prepare_proposal",
    "review_manually": "review_manually",
    "opportunity_review": "opportunity_review",
    "qualification_review": "qualification_review",
    "pricing_review": "pricing_review",
}


def _infer_task_type(recommendation_type: str) -> str:
    if recommendation_type in TASK_TYPE_MAP:
        return recommendation_type
    return "review_manually"


def _build_task_title(rec: AIRecommendation) -> str:
    text = (rec.recommendation_text or "").strip()
    if not text:
        return f"Review {rec.recommendation_type}"
    return text[:255]


def materialize_recommendation_to_task(rec: AIRecommendation) -> CRMTask:
    existing = CRMTask.objects.filter(source_recommendation=rec).order_by("-created_at").first()
    if existing is not None:
        if rec.status != AIRecommendation.STATUS_MATERIALIZED:
            rec.status = AIRecommendation.STATUS_MATERIALIZED
            rec.save(update_fields=["status"])
        return existing

    task = CRMTask.objects.create(
        source_recommendation=rec,
        title=_build_task_title(rec),
        description=rec.recommendation_text or "",
        task_type=_infer_task_type(rec.recommendation_type),
        source="auto",
        source_action=rec.recommendation_type,
        priority="normal",
    )

    rec.status = AIRecommendation.STATUS_MATERIALIZED
    rec.save(update_fields=["status"])

    print(f"[FLOW] Recommendation materialized_to_task rec_id={rec.id} task_id={task.id}")
    return task


def materialize_recommendation_as_task(rec: AIRecommendation) -> CRMTask:
    return materialize_recommendation_to_task(rec)


def materialize_recommendation(rec: AIRecommendation) -> CRMTask:
    return materialize_recommendation_to_task(rec)


def materialize_open_recommendations(queryset=None) -> int:
    queryset = queryset or AIRecommendation.objects.filter(status=AIRecommendation.STATUS_NEW)
    count = 0

    for rec in queryset:
        materialize_recommendation_to_task(rec)
        count += 1

    return count
