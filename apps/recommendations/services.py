from apps.recommendations.models import AIRecommendation
from apps.tasks_app.models import CRMTask


def dismiss_recommendation(recommendation: AIRecommendation):
    if recommendation.status in ["dismissed", "executed"]:
        return recommendation, False

    recommendation.status = "dismissed"
    recommendation.save(update_fields=["status"])

    return recommendation, True


def materialize_recommendation(recommendation: AIRecommendation):
    existing = CRMTask.objects.filter(source_recommendation=recommendation).first()

    if existing:
        if recommendation.status != "materialized":
            recommendation.status = "materialized"
            recommendation.save(update_fields=["status"])
        return existing, False

    task = CRMTask.objects.create(
        source_recommendation=recommendation,
        title=recommendation.recommendation_text[:200],
        description=recommendation.recommendation_text,
        task_type=recommendation.recommendation_type,
        status="open",
        priority="normal",
    )

    recommendation.status = "materialized"
    recommendation.save(update_fields=["status"])

    return task, True
