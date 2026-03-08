from __future__ import annotations

from dataclasses import dataclass

from django.apps import apps
from django.db import transaction


@dataclass
class RecommendationCandidate:
    recommendation_type: str
    recommendation_text: str
    confidence: float


def _model(app_label: str, model_name: str):
    return apps.get_model(app_label, model_name)


def _event_recorder():
    try:
        from services.events import record_event  # type: ignore
        return record_event
    except Exception:
        return None


def _candidate_from_inference(inference) -> RecommendationCandidate | None:
    inference_type = getattr(inference, "inference_type", "")
    inference_value = getattr(inference, "inference_value", {}) or {}
    confidence = float(getattr(inference, "confidence", 0.70) or 0.70)

    if inference_type == "contact_role_fit" and inference_value.get("status") == "redirected":
        return RecommendationCandidate(
            recommendation_type="contact_strategy",
            recommendation_text="Buscar o validar otro interlocutor antes de seguir con este contacto.",
            confidence=confidence,
        )

    if inference_type == "next_best_action":
        action = inference_value.get("action")

        if action == "find_alternative_contact":
            return RecommendationCandidate(
                recommendation_type="next_action",
                recommendation_text="Identificar un interlocutor alternativo o pedir redirección explícita.",
                confidence=confidence,
            )

        if action == "follow_up_later":
            suggested_timing = inference_value.get("suggested_timing", "más adelante")
            return RecommendationCandidate(
                recommendation_type="followup",
                recommendation_text=f"No insistir ahora. Retomar el contacto en {suggested_timing}.",
                confidence=confidence,
            )

        if action == "reply_with_scope_clarification":
            return RecommendationCandidate(
                recommendation_type="reply_strategy",
                recommendation_text="Preparar respuesta aclarando alcance y validando necesidad antes de avanzar.",
                confidence=confidence,
            )

    if inference_type == "interest_level":
        level = inference_value.get("level")

        if level == "moderate":
            return RecommendationCandidate(
                recommendation_type="qualification",
                recommendation_text="Responder con explicación breve del servicio y una pregunta de cualificación.",
                confidence=confidence,
            )

        if level == "weak_or_ambiguous":
            return RecommendationCandidate(
                recommendation_type="hold",
                recommendation_text="No abrir oportunidad todavía. Mantener seguimiento ligero hasta obtener más señal.",
                confidence=confidence,
            )

    if inference_type == "opportunity_probability" and inference_value.get("status") == "emerging_signal":
        return RecommendationCandidate(
            recommendation_type="opportunity_review",
            recommendation_text="Revisar apertura de oportunidad y dejar claro el siguiente paso comercial.",
            confidence=confidence,
        )

    if inference_type == "pricing_objection":
        return RecommendationCandidate(
            recommendation_type="pricing_strategy",
            recommendation_text="Responder enmarcando primero el alcance antes de discutir precio cerrado.",
            confidence=confidence,
        )

    if inference_type == "relationship_temperature" and inference_value.get("temperature") == "deferred_not_rejected":
        return RecommendationCandidate(
            recommendation_type="timing_strategy",
            recommendation_text="Mantener el caso vivo pero diferido. Programar seguimiento en la ventana indicada.",
            confidence=confidence,
        )

    return None


@transaction.atomic
def create_recommendation_from_inference(inference):
    RecommendationModel = _model("recommendations", "AIRecommendation")
    record_event = _event_recorder()

    candidate = _candidate_from_inference(inference)
    if candidate is None:
        return None

    existing = RecommendationModel.objects.filter(
        scope_type="inference_record",
        scope_id=inference.id,
        recommendation_type=candidate.recommendation_type,
        recommendation_text=candidate.recommendation_text,
    ).first()
    if existing:
        return existing

    recommendation = RecommendationModel.objects.create(
        scope_type="inference_record",
        scope_id=inference.id,
        recommendation_type=candidate.recommendation_type,
        recommendation_text=candidate.recommendation_text,
        confidence=candidate.confidence,
        status="active",
    )

    if callable(record_event):
        try:
            record_event(
                event_type="recommendation_created",
                aggregate_type="ai_recommendation",
                aggregate_id=recommendation.id,
                payload={
                    "recommendation_type": candidate.recommendation_type,
                    "source_inference_id": inference.id,
                },
                triggered_by_type="system",
                triggered_by_id=None,
            )
        except Exception:
            pass

    return recommendation
