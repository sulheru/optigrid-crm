from typing import Any
from .models import CRMUpdateProposal
from apps.inferences.models import InferenceRecord


def create_basic_proposal(email: Any) -> None:
    if email is None:
        return

    source_id = str(getattr(email, "id", ""))

    # 🔍 Detectar signals
    has_pricing_signal = InferenceRecord.objects.filter(
        source_type="inbound_email",
        source_id=source_id,
        inference_type="pricing_interest_signal",
    ).exists()

    # 🎯 Decidir proposal
    if has_pricing_signal:
        proposal_type = "prepare_pricing_response"
        payload = {"reason": "pricing_detected"}
    else:
        proposal_type = "review_email"
        payload = {"reason": "new_email_detected"}

    CRMUpdateProposal.objects.get_or_create(
        source_type="inbound_email",
        source_id=source_id,
        proposal_type=proposal_type,
        defaults={
            "payload": payload,
            "status": "proposed",
        },
    )
