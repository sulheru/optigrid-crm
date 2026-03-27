from pathlib import Path

path = Path("apps/external_actions/tests.py")
text = path.read_text()

start_marker = "from apps.recommendations.models import AIRecommendation"
end_marker = "class RecommendationExternalBridgeTests(TestCase):"

if start_marker not in text or end_marker not in text:
    raise SystemExit("No se encontraron los marcadores esperados en apps/external_actions/tests.py")

start = text.index(start_marker)
end = text.index(end_marker)

replacement = """from apps.recommendations.models import AIRecommendation
from apps.recommendations.services.external_actions import (
    ensure_external_action_intent_for_recommendation,
    get_open_external_intent_for_recommendation,
    recommendation_supports_external_intent,
)


def _make_recommendation(**overrides):
    field_names = {f.name for f in AIRecommendation._meta.get_fields() if getattr(f, "concrete", False)}

    payload = {}

    # Campo base esperado por el sistema actual
    if "recommendation_type" in field_names:
        payload["recommendation_type"] = overrides.get("recommendation_type", "followup")

    # Campos opcionales: solo si existen en el modelo real
    optional_candidates = {
        "title": overrides.get("title", "Follow up with contact"),
        "name": overrides.get("title", "Follow up with contact"),
        "summary": overrides.get("content", "Prepare a polite follow-up."),
        "content": overrides.get("content", "Prepare a polite follow-up."),
        "description": overrides.get("content", "Prepare a polite follow-up."),
        "message": overrides.get("content", "Prepare a polite follow-up."),
        "body": overrides.get("content", "Prepare a polite follow-up."),
        "rationale": overrides.get("rationale", "No reply in thread."),
        "reasoning": overrides.get("rationale", "No reply in thread."),
        "explanation": overrides.get("rationale", "No reply in thread."),
        "status": overrides.get("status", "new"),
        "confidence": overrides.get("confidence", 0.75),
        "metadata": overrides.get("metadata", {"target_email": "test@example.com"}),
        "payload": overrides.get("metadata", {"target_email": "test@example.com"}),
        "data": overrides.get("metadata", {"target_email": "test@example.com"}),
    }

    for key, value in optional_candidates.items():
        if key in field_names:
            payload[key] = value

    # Si el modelo exige campos adicionales no nulos sin default,
    # los rellenamos de forma conservadora.
    for field in AIRecommendation._meta.fields:
        if field.auto_created:
            continue
        if field.name in payload:
            continue
        if field.null:
            continue
        if field.has_default():
            continue
        if getattr(field, "blank", False):
            if field.get_internal_type() in {"CharField", "TextField"}:
                payload[field.name] = ""
                continue

        internal_type = field.get_internal_type()

        if internal_type in {"CharField", "TextField"}:
            payload[field.name] = ""
        elif internal_type in {"IntegerField", "BigIntegerField", "PositiveIntegerField", "SmallIntegerField"}:
            payload[field.name] = 0
        elif internal_type in {"FloatField", "DecimalField"}:
            payload[field.name] = 0
        elif internal_type == "BooleanField":
            payload[field.name] = False

    payload.update(overrides)
    return AIRecommendation.objects.create(**payload)


"""

new_text = text[:start] + replacement + text[end:]
path.write_text(new_text)
print("[ok] helper _make_recommendation insertado en apps/external_actions/tests.py")
