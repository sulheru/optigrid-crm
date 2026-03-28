import hashlib

from apps.knowledge.models import KnowledgeCandidate
from apps.knowledge.services.embeddings import upsert_vector_memory


SUCCESS_VALUES = {"succeeded", "success", "completed", "executed", "done", "sent"}


def on_external_action_executed(intent):
    """
    Hook tolerante y de bajo riesgo.
    V1:
    - persiste memoria vectorial del intento ejecutado
    - si detecta repetición semántica, propone capability_proposal de baja confianza
    """
    if intent is None:
        return None

    execution_status = str(getattr(intent, "execution_status", "") or "").lower()
    if execution_status not in SUCCESS_VALUES:
        return None

    action_type = getattr(intent, "action_type", None) or getattr(intent, "intent_type", None) or "external_action"
    payload = getattr(intent, "payload", None) or getattr(intent, "request_payload", None) or {}
    recommendation_id = getattr(intent, "recommendation_id", None)

    text = (
        f"Executed external action\n"
        f"action_type={action_type}\n"
        f"recommendation_id={recommendation_id}\n"
        f"payload={payload}\n"
    )

    upsert_vector_memory(
        namespace="external_action_execution",
        source_model=intent.__class__._meta.label,
        source_pk=str(getattr(intent, "pk", "")),
        source_text=text,
        metadata={
            "action_type": str(action_type),
            "recommendation_id": recommendation_id,
            "execution_status": execution_status,
        },
    )

    signature = hashlib.sha256(
        f"{action_type}|{str(payload)[:500]}".encode("utf-8")
    ).hexdigest()

    candidate, _ = KnowledgeCandidate.objects.get_or_create(
        source_signature=signature,
        defaults={
            "candidate_type": KnowledgeCandidate.CandidateType.CAPABILITY_PROPOSAL,
            "content": (
                "Observed successful external action.\n\n"
                f"Action type:\n{action_type}\n\n"
                "Suggested capability:\n"
                "Consider a future automation or reusable capability around this executed pattern.\n"
            ),
            "confidence_score": 0.35,
            "source_examples": [
                {
                    "source_model": intent.__class__._meta.label,
                    "source_pk": getattr(intent, "pk", None),
                    "action_type": action_type,
                    "payload_preview": str(payload)[:400],
                }
            ],
            "metadata": {
                "title": f"Capability from executed action: {action_type}",
                "source_kind": "external_action_hook",
                "execution_status": execution_status,
            },
        },
    )
    return candidate
