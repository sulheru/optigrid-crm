from apps.recommendations.models import AIRecommendation
from apps.tasks.models import CRMTask


def recommendation_to_task_payload(recommendation: AIRecommendation) -> dict:
    rec_type = (recommendation.recommendation_type or "").strip().lower()
    rec_text = recommendation.recommendation_text or ""

    task_type = "review_manually"
    title = "Revisar recomendación IA"
    description = rec_text
    priority = "normal"

    if "reply" in rec_type or "respond" in rec_type:
        task_type = "reply_email"
        title = "Responder email recomendado por IA"
        priority = "high"
    elif "follow" in rec_type:
        task_type = "follow_up"
        title = "Hacer follow-up"
        priority = "high"
    elif "call" in rec_type or "meeting" in rec_type:
        task_type = "schedule_call"
        title = "Agendar llamada"
        priority = "high"
    elif "proposal" in rec_type or "quote" in rec_type or "offer" in rec_type:
        task_type = "prepare_proposal"
        title = "Preparar propuesta comercial"
        priority = "high"

    return {
        "title": title,
        "description": description,
        "task_type": task_type,
        "priority": priority,
    }


def materialize_recommendation_as_task(recommendation: AIRecommendation) -> CRMTask:
    existing = CRMTask.objects.filter(source_recommendation=recommendation).first()
    if existing:
        return existing

    payload = recommendation_to_task_payload(recommendation)

    task = CRMTask.objects.create(
        source_recommendation=recommendation,
        title=payload["title"],
        description=payload["description"],
        task_type=payload["task_type"],
        priority=payload["priority"],
        status="open",
    )

    if hasattr(recommendation, "status") and recommendation.status in ("new", "open", "pending"):
        recommendation.status = "materialized"
        recommendation.save(update_fields=["status"])

    return task
