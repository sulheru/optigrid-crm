from typing import Any
from .models import InferenceRecord


PRICING_KEYWORDS = {"price", "pricing", "cost", "budget", "precio", "presupuesto"}


def create_basic_email_inference(email: Any) -> None:
    if email is None:
        return

    body = getattr(email, "body", "") or ""
    body_lower = body.lower()

    source_id = str(getattr(email, "id", ""))  # 🔴 IMPORTANTE: string consistente

    def contains_any(keywords):
        return any(k in body_lower for k in keywords)

    # Base
    InferenceRecord.objects.get_or_create(
        source_type="inbound_email",
        source_id=source_id,
        inference_type="email_has_content",
        defaults={
            "payload": {"length": len(body)},
            "confidence": 0.7,
        },
    )

    if contains_any(PRICING_KEYWORDS):
        InferenceRecord.objects.get_or_create(
            source_type="inbound_email",
            source_id=source_id,
            inference_type="pricing_interest_signal",
            defaults={
                "payload": {},
                "confidence": 0.75,
            },
        )
