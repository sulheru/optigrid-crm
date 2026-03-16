from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

from django.utils import timezone


@dataclass
class GeneratedRecommendation:
    recommendation_type: str
    recommendation_text: str
    rationale: str
    priority: str
    confidence: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _lower(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().lower()


def _contains_any(haystack: str, needles: list[str]) -> bool:
    haystack = _lower(haystack)
    return any(needle in haystack for needle in needles)


def _collect_text_blobs(context: dict[str, Any]) -> list[str]:
    blobs: list[str] = []

    opportunity = context.get("opportunity") or {}
    for key in ("title", "company_name", "summary"):
        blobs.append(str(opportunity.get(key) or ""))

    source_task = context.get("source_task") or {}
    for key in ("task_type", "title", "description", "status"):
        blobs.append(str(source_task.get(key) or ""))

    source_recommendation = context.get("source_recommendation") or {}
    for key in ("recommendation_text", "recommendation_type"):
        blobs.append(str(source_recommendation.get(key) or ""))

    proposal = context.get("proposal") or {}
    for key in ("proposed_change_type", "proposed_payload", "proposal_status"):
        blobs.append(str(proposal.get(key) or ""))

    for item in context.get("inferences") or []:
        blobs.append(str(item.get("inference_type") or ""))
        blobs.append(str(item.get("inference_value") or ""))
        blobs.append(str(item.get("rationale") or ""))

    for item in context.get("facts") or []:
        blobs.append(str(item.get("fact_type") or ""))
        blobs.append(str(item.get("fact_value") or ""))

    for item in context.get("emails") or []:
        blobs.append(str(item.get("subject") or ""))
        blobs.append(str(item.get("body_text") or ""))

    return blobs


def _has_live_question_in_recent_email(context: dict[str, Any]) -> bool:
    for email in reversed(context.get("emails") or []):
        body = _lower(email.get("body_text"))
        subject = _lower(email.get("subject"))
        if "?" in body or "?" in subject:
            return True
    return False


def _latest_email_timestamp(context: dict[str, Any]):
    latest = None
    for email in context.get("emails") or []:
        value = email.get("sent_at")
        if not value:
            continue
        try:
            dt = timezone.datetime.fromisoformat(value.replace("Z", "+00:00"))
            if latest is None or dt > latest:
                latest = dt
        except Exception:
            continue
    return latest


def analyze_opportunity_context(context: dict[str, Any]) -> list[dict[str, Any]]:
    results: list[GeneratedRecommendation] = []
    blobs = _collect_text_blobs(context)
    corpus = "\n".join(blobs)

    opportunity = context.get("opportunity") or {}
    stage = _lower(opportunity.get("stage"))
    now = timezone.now()

    latest_email_dt = _latest_email_timestamp(context)
    inactive_days = None
    if latest_email_dt is not None:
        try:
            inactive_days = (now - latest_email_dt).days
        except Exception:
            inactive_days = None

    has_price_signal = _contains_any(
        corpus,
        ["precio", "coste", "cost", "budget", "presupuesto", "pricing", "tarifa", "fee", "quote"],
    )

    has_risk_signal = _contains_any(
        corpus,
        [
            "no ahora",
            "más adelante",
            "mas adelante",
            "retomar",
            "mayo",
            "may",
            "later",
            "not now",
            "sin respuesta",
            "objec",
            "riesgo",
            "risk",
            "too expensive",
            "caro",
        ],
    )

    has_interest_signal = _contains_any(
        corpus,
        [
            "interés",
            "interest",
            "podríamos valorar",
            "podriamos valorar",
            "sounds interesting",
            "nos podría interesar",
            "nos podria interesar",
            "review inicial",
            "revisión inicial",
        ],
    )

    has_question_signal = _has_live_question_in_recent_email(context)

    if has_price_signal and stage in {"qualified", "proposal", "new"}:
        results.append(
            GeneratedRecommendation(
                recommendation_type="pricing_strategy",
                recommendation_text="Preparar estrategia de precio basada en alcance antes de fijar cifra cerrada.",
                rationale="Hay señales de precio o presupuesto en el contexto.",
                priority="high",
                confidence=0.82,
            )
        )

    if has_question_signal:
        results.append(
            GeneratedRecommendation(
                recommendation_type="reply_strategy",
                recommendation_text="Responder a las preguntas abiertas con una propuesta de siguiente paso concreta.",
                rationale="La conversación parece viva y requiere respuesta humana clara.",
                priority="high",
                confidence=0.86,
            )
        )

    if inactive_days is not None and inactive_days >= 7 and stage not in {"won", "lost"}:
        results.append(
            GeneratedRecommendation(
                recommendation_type="followup",
                recommendation_text="Lanzar follow-up breve y contextual para reactivar la conversación.",
                rationale=f"No se detecta actividad reciente desde hace {inactive_days} días.",
                priority="medium",
                confidence=0.79,
            )
        )

    if has_risk_signal:
        results.append(
            GeneratedRecommendation(
                recommendation_type="risk_flag",
                recommendation_text="Revisar riesgo comercial y validar si el stage actual sigue reflejando la realidad.",
                rationale="El contexto contiene señales de espera, aplazamiento o fricción.",
                priority="high",
                confidence=0.77,
            )
        )

    next_action_text = "Revisar oportunidad y definir siguiente paso manual."
    next_action_rationale = "No se detectó una señal dominante única; conviene mantener control humano."

    if has_question_signal:
        next_action_text = "Preparar respuesta breve que conteste la pregunta abierta y cierre con una propuesta de call o siguiente paso."
        next_action_rationale = "La mejor acción inmediata es responder mientras la conversación sigue viva."
    elif has_price_signal:
        next_action_text = "Preparar mensaje de cualificación orientado a alcance y contexto antes de entrar en precio final."
        next_action_rationale = "La conversación apunta a precio y conviene proteger el encuadre comercial."
    elif has_risk_signal:
        next_action_text = "No insistir ahora; registrar recordatorio y retomar el contacto cuando venza la ventana indicada por el contexto."
        next_action_rationale = "La oportunidad contiene señales explícitas de aplazamiento."
    elif has_interest_signal:
        next_action_text = "Avanzar cualificación con 1-3 preguntas de alcance y decisión."
        next_action_rationale = "Se detecta interés comercial suficiente para profundizar."

    results.append(
        GeneratedRecommendation(
            recommendation_type="next_action",
            recommendation_text=next_action_text,
            rationale=next_action_rationale,
            priority="high",
            confidence=0.88,
        )
    )

    deduped: list[GeneratedRecommendation] = []
    seen: set[tuple[str, str]] = set()
    for item in results:
        key = (item.recommendation_type, item.recommendation_text.strip().lower())
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)

    return [item.to_dict() for item in deduped]
