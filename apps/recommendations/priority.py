# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/recommendations/priority.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
from datetime import timedelta
from django.utils import timezone


TYPE_WEIGHTS = {
    "followup": 25,
    "reply_strategy": 25,
    "contact_strategy": 20,
    "opportunity_review": 20,
    "next_action": 15,
    "qualification": 10,
    "risk_flag": 20,
    "hold": -10,
}


def compute_priority_score(recommendation):
    if recommendation.status != "new":
        return 0

    score = 0

    confidence = recommendation.confidence or 0
    score += confidence * 50

    now = timezone.now()
    created_at = getattr(recommendation, "created_at", None)

    if created_at:
        delta = now - created_at
        if delta < timedelta(hours=1):
            score += 30
        elif delta < timedelta(hours=24):
            score += 20
        elif delta < timedelta(days=3):
            score += 10

    score += TYPE_WEIGHTS.get(recommendation.recommendation_type, 5)

    return round(score, 2)
