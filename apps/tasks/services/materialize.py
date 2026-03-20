# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/tasks/services/materialize.py
from apps.recommendations.models import AIRecommendation
from apps.tasks.models import CRMTask


EXACT_TASK_TYPE_MAP = {
    "reply_strategy": ("reply_email", "Responder email recomendado por IA", "high"),
    "followup": ("follow_up", "Hacer follow-up", "high"),
    "schedule_call": ("schedule_call", "Agendar llamada", "high"),
    "prepare_proposal": ("prepare_proposal", "Preparar propuesta comercial", "high"),
    "qualification": ("qualification_review", "Revisar cualificación comercial", "normal"),
    "opportunity_review": ("opportunity_review", "Revisar oportunidad detectada por IA", "high"),
    "pricing_strategy": ("pricing_review", "Revisar estrategia de pricing", "normal"),
}

KEYWORD_FALLBACKS = [
    (("reply", "respond"), ("reply_email", "Responder email recomendado por IA", "high")),
    (("follow",), ("follow_up", "Hacer follow-up", "high")),
    (("call", "meeting"), ("schedule_call", "Agendar llamada", "high")),
    (("proposal", "quote", "offer"), ("prepare_proposal", "Preparar propuesta comercial", "high")),
    (("qualif",), ("qualification_review", "Revisar cualificación comercial", "normal")),
    (("opportunity",), ("opportunity_review", "Revisar oportunidad detectada por IA", "high")),
    (("pricing", "price", "budget"), ("pricing_review", "Revisar estrategia de pricing", "normal")),
]


def recommendation_to_task_payload(recommendation: AIRecommendation) -> dict:
    rec_type = (recommendation.recommendation_type or "").strip().lower()
    rec_text = recommendation.recommendation_text or ""

    mapped = EXACT_TASK_TYPE_MAP.get(rec_type)
    if mapped is not None:
        task_type, title, priority = mapped
        return {
            "title": title,
            "description": rec_text,
            "task_type": task_type,
            "priority": priority,
        }

    for keywords, payload in KEYWORD_FALLBACKS:
        if any(keyword in rec_type for keyword in keywords):
            task_type, title, priority = payload
            return {
                "title": title,
                "description": rec_text,
                "task_type": task_type,
                "priority": priority,
            }

    return {
        "title": "Revisar recomendación IA",
        "description": rec_text,
        "task_type": "review_manually",
        "priority": "normal",
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
