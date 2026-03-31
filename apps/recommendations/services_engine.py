from typing import Any

from .models import AIRecommendation


def create_basic_email_recommendation(email: Any) -> None:
    if email is None:
        return

    email_id = getattr(email, "id", None)
    body = (getattr(email, "body", "") or "").lower()

    recommendation_type = "review_email"
    recommendation_text = "Nuevo email procesado. Revisar contexto y decidir siguiente accion."

    if any(token in body for token in ["call", "meeting", "meet", "reunión", "llamada"]):
        recommendation_type = "followup"
        recommendation_text = "El email sugiere interes en conversación. Valorar propuesta de llamada."
    elif any(token in body for token in ["price", "pricing", "cost", "budget", "precio", "presupuesto"]):
        recommendation_type = "reply_strategy"
        recommendation_text = "El email sugiere interes en precio o presupuesto. Preparar respuesta de encuadre comercial."
    elif any(token in body for token in ["later", "next month", "next quarter", "mayo", "más adelante", "mas adelante"]):
        recommendation_type = "followup"
        recommendation_text = "El email sugiere timing diferido. Valorar seguimiento futuro en vez de respuesta inmediata."

    candidate_payload = {
        "scope_type": "inbound_email",
        "scope_id": email_id,
        "recommendation_type": recommendation_type,
        "recommendation_text": recommendation_text,
        "confidence": 0.6,
        "status": "active",
        "source": "crm_update_engine",
    }

    model_fields = {field.name for field in AIRecommendation._meta.fields}
    payload = {k: v for k, v in candidate_payload.items() if k in model_fields}

    lookup = {}
    for key in ("scope_type", "scope_id", "recommendation_type", "source"):
        if key in payload:
            lookup[key] = payload[key]

    defaults = {k: v for k, v in payload.items() if k not in lookup}

    if lookup:
        AIRecommendation.objects.get_or_create(**lookup, defaults=defaults)
    else:
        AIRecommendation.objects.create(**payload)
