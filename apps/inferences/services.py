from __future__ import annotations

from apps.inferences.models import InferenceRecord
from apps.recommendations.services import create_recommendation_from_inference
from apps.recommendations.services_llm import create_recommendations_from_llm_output
from services.ai.llm_client import LLMClient
from apps.recommendations.merge_runtime import merge_persisted_recommendations_for_scope


def create_inference_record(
    *,
    source_type: str,
    source_id: int,
    inference_type: str,
    inference_value: dict | None = None,
    confidence: float = 0.7,
) -> InferenceRecord:
    """
    Persistencia pura de la inference.
    """
    return InferenceRecord.objects.create(
        source_type=source_type,
        source_id=source_id,
        inference_type=inference_type,
        inference_value=inference_value or {},
        confidence=confidence,
    )



def create_inference(
    *,
    source_type: str,
    source_id: int,
    input_text: str,
) -> list[InferenceRecord]:
    """
    Nuevo entrypoint IA-first.

    - usa LLMProvider (vía LLMClient)
    - genera inferencias
    - persiste resultados
    - dispara recommendations
    """

    llm = LLMClient()
    result = llm.analyze_email(input_text)

    created = []

    for inf in result.get("inferences", []):
        record = create_inference_record(
            source_type=source_type,
            source_id=source_id,
            inference_type=inf.get("type", "unknown"),
            inference_value=inf,
            confidence=inf.get("confidence", 0.7),
        )

        try:
            create_recommendation_from_inference(record)
        except Exception:
            pass

        created.append(record)

    # --- NEW: LLM DIRECT RECOMMENDATIONS ---
    try:
        from apps.recommendations.services_llm import create_recommendations_from_llm_output

        create_recommendations_from_llm_output(
            scope_type=source_type,
            scope_id=source_id,
            llm_result=result,
        )

        merge_persisted_recommendations_for_scope(
            scope_type=record.source_type,
            scope_id=record.source_id,
        )
    except Exception:
        pass

    return created

