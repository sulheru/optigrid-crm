from __future__ import annotations

from apps.recommendations.merge import merge_recommendation_candidates
from apps.recommendations.models import AIRecommendation


def merge_persisted_recommendations_for_scope(scope_type: str, scope_id) -> list[AIRecommendation]:
    candidates = list(
        AIRecommendation.objects.filter(
            scope_type=scope_type,
            scope_id=str(scope_id),
            status=AIRecommendation.STATUS_NEW,
        ).order_by("id")
    )

    if len(candidates) <= 1:
        return candidates

    result = merge_recommendation_candidates(candidates)
    kept = result.kept
    dismissed = result.dismissed

    persisted_kept: list[AIRecommendation] = []

    for rec in kept:
        if rec.pk:
            if rec.source != AIRecommendation.SOURCE_MERGED:
                rec.source = rec.source or AIRecommendation.SOURCE_RULES
                rec.save(update_fields=["source"])
            persisted_kept.append(rec)
            continue

        persisted_kept.append(
            AIRecommendation.objects.create(
                scope_type=rec.scope_type,
                scope_id=str(rec.scope_id),
                recommendation_type=rec.recommendation_type,
                recommendation_text=rec.recommendation_text,
                confidence=rec.confidence,
                status=getattr(rec, "status", AIRecommendation.STATUS_NEW) or AIRecommendation.STATUS_NEW,
                source=getattr(rec, "source", AIRecommendation.SOURCE_MERGED) or AIRecommendation.SOURCE_MERGED,
            )
        )

    dismissed_ids = [rec.pk for rec in dismissed if getattr(rec, "pk", None)]
    if dismissed_ids:
        AIRecommendation.objects.filter(id__in=dismissed_ids).exclude(
            id__in=[rec.id for rec in persisted_kept if getattr(rec, "id", None)]
        ).update(status=AIRecommendation.STATUS_DISMISSED)

    return persisted_kept
