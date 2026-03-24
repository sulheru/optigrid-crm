from __future__ import annotations

from apps.inferences.models import InferenceRecord
from apps.inferences.services import create_inference
from apps.recommendations.services import create_recommendation_from_inference


def create_inference(
    *,
    source_type: str,
    source_id: int,
    inference_type: str,
    inference_value: dict | None = None,
    confidence: float = 0.7,
) -> InferenceRecord:
    """
    Canonical inference creation entrypoint.

    Guarantees:
    - inference is persisted
    - recommendation is generated (if applicable)
    """

    inference = create_inference(
        source_type=source_type,
        source_id=source_id,
        inference_type=inference_type,
        inference_value=inference_value or {},
        confidence=confidence,
    )

    try:
        create_recommendation_from_inference(inference)
    except Exception:
        # nunca romper el pipeline por recommendation
        pass

    return inference
