# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/services/inference_engine.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from apps.facts.models import FactRecord
from apps.inferences.models import InferenceRecord


@dataclass
class InferenceCandidate:
    inference_type: str
    inference_value: dict[str, Any]
    confidence: float
    rationale: str


def infer_from_fact(fact: FactRecord) -> list[InferenceCandidate]:
    """
    Convierte un hecho en una o varias inferencias operativas.
    """
    out: list[InferenceCandidate] = []

    if fact.fact_type == "redirect_statement":
        out.append(
            InferenceCandidate(
                inference_type="contact_role_fit",
                inference_value={
                    "status": "redirected",
                    "contact_role_fit": "low",
                },
                confidence=0.93,
                rationale="El mensaje indica explícitamente que el interlocutor no es la persona adecuada.",
            )
        )
        out.append(
            InferenceCandidate(
                inference_type="next_best_action",
                inference_value={
                    "action": "find_alternative_contact",
                },
                confidence=0.90,
                rationale="Si el contacto actual redirige, la siguiente acción útil es identificar al interlocutor correcto.",
            )
        )

    elif fact.fact_type == "timing_statement":
        out.append(
            InferenceCandidate(
                inference_type="next_best_action",
                inference_value={
                    "action": "follow_up_later",
                    "suggested_timing": "may",
                },
                confidence=0.95,
                rationale="El email marca una ventana temporal explícita para retomar el contacto.",
            )
        )
        out.append(
            InferenceCandidate(
                inference_type="relationship_temperature",
                inference_value={
                    "temperature": "deferred_not_rejected",
                },
                confidence=0.82,
                rationale="No hay rechazo total; hay aplazamiento con momento futuro indicado.",
            )
        )

    elif fact.fact_type == "interest_statement":
        out.append(
            InferenceCandidate(
                inference_type="interest_level",
                inference_value={
                    "level": "moderate",
                },
                confidence=0.82,
                rationale="El email expresa interés explícito o disposición a valorar una revisión inicial.",
            )
        )

    elif fact.fact_type == "scope_statement":
        out.append(
            InferenceCandidate(
                inference_type="opportunity_probability",
                inference_value={
                    "status": "emerging_signal",
                    "signal_strength": "moderate",
                },
                confidence=0.80,
                rationale="Preguntar por alcance suele ser una señal comercial relevante, aunque aún temprana.",
            )
        )
        out.append(
            InferenceCandidate(
                inference_type="next_best_action",
                inference_value={
                    "action": "reply_with_scope_clarification",
                },
                confidence=0.84,
                rationale="La mejor respuesta operativa es aclarar alcance antes de avanzar.",
            )
        )

    elif fact.fact_type == "budget_statement":
        out.append(
            InferenceCandidate(
                inference_type="pricing_objection",
                inference_value={
                    "status": "budget_or_price_signal",
                },
                confidence=0.78,
                rationale="La mención de presupuesto o precio introduce sensibilidad económica en la conversación.",
            )
        )

    elif fact.fact_type == "light_reply_statement":
        out.append(
            InferenceCandidate(
                inference_type="interest_level",
                inference_value={
                    "level": "weak_or_ambiguous",
                },
                confidence=0.65,
                rationale="Una respuesta breve y cortés no es suficiente por sí sola para concluir interés fuerte.",
            )
        )

    return out


def create_inferences_from_fact(fact: FactRecord) -> list[InferenceRecord]:
    created: list[InferenceRecord] = []

    for candidate in infer_from_fact(fact):
        record = InferenceRecord.objects.create(
            source_type="fact_record",
            source_id=fact.id,
            inference_type=candidate.inference_type,
            inference_value=candidate.inference_value,
            confidence=candidate.confidence,
            rationale=candidate.rationale,
        )
        created.append(record)

    return created
