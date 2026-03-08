from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.utils import timezone

from apps.emailing.models import EmailMessage
from apps.facts.models import FactRecord


@dataclass
class ExtractedFact:
    fact_type: str
    fact_value: dict[str, Any]
    confidence: float


def _normalize_text(text: str) -> str:
    return (text or "").strip()


def _email_datetime(email: EmailMessage):
    """
    Devuelve la mejor fecha disponible sin asumir nombres de campo concretos.
    """
    for field_name in ("received_at", "sent_at", "created_at", "updated_at"):
        value = getattr(email, field_name, None)
        if value is not None:
            return value
    return timezone.now()


def extract_fact_candidates_from_email(email: EmailMessage) -> list[ExtractedFact]:
    """
    Extracción heurística mínima para el vertical slice inicial.

    Regla:
    - solo hechos observables
    - no inferencias aquí
    """
    body_text = getattr(email, "body_text", "") or ""
    subject = getattr(email, "subject", "") or ""

    text = _normalize_text(body_text).lower()
    subject_lc = _normalize_text(subject).lower()

    candidates: list[ExtractedFact] = []

    if not text and not subject_lc:
        return candidates

    if "no soy la persona adecuada" in text or "no llevo esta parte" in text:
        candidates.append(
            ExtractedFact(
                fact_type="redirect_statement",
                fact_value={
                    "kind": "redirect_statement",
                    "evidence": "contact_not_right_person",
                    "source_text": body_text,
                },
                confidence=0.95,
            )
        )

    if "escríbeme en mayo" in text or "escribeme en mayo" in text:
        candidates.append(
            ExtractedFact(
                fact_type="timing_statement",
                fact_value={
                    "kind": "timing_statement",
                    "timing": "may",
                    "source_text": body_text,
                },
                confidence=0.95,
            )
        )

    if "nos interesa" in text or "podríamos valorar" in text or "podriamos valorar" in text:
        candidates.append(
            ExtractedFact(
                fact_type="interest_statement",
                fact_value={
                    "kind": "interest_statement",
                    "signal": "expressed_interest",
                    "source_text": body_text,
                },
                confidence=0.85,
            )
        )

    if "qué incluiría" in text or "que incluiria" in text or "alcance" in text:
        candidates.append(
            ExtractedFact(
                fact_type="scope_statement",
                fact_value={
                    "kind": "scope_statement",
                    "signal": "asks_about_scope",
                    "source_text": body_text,
                },
                confidence=0.85,
            )
        )

    if "presupuesto" in text or "coste" in text or "precio" in text:
        candidates.append(
            ExtractedFact(
                fact_type="budget_statement",
                fact_value={
                    "kind": "budget_statement",
                    "signal": "budget_or_price_mentioned",
                    "source_text": body_text,
                },
                confidence=0.80,
            )
        )

    if "gracias" in text and len(text) < 80:
        candidates.append(
            ExtractedFact(
                fact_type="light_reply_statement",
                fact_value={
                    "kind": "light_reply_statement",
                    "signal": "light_polite_reply",
                    "source_text": body_text,
                },
                confidence=0.70,
            )
        )

    return candidates


def create_facts_from_email(email: EmailMessage) -> list[FactRecord]:
    """
    Materializa hechos estructurados desde un EmailMessage.
    """
    created: list[FactRecord] = []
    candidates = extract_fact_candidates_from_email(email)
    observed_at = _email_datetime(email)

    for candidate in candidates:
        fact = FactRecord.objects.create(
            source_type="email_message",
            source_id=email.id,
            fact_type=candidate.fact_type,
            fact_value=candidate.fact_value,
            observed_at=observed_at,
            confidence=candidate.confidence,
        )
        created.append(fact)

    return created
