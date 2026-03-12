from decimal import Decimal, InvalidOperation

from apps.inferences.models import InferenceRecord


def _as_dict(value):
    return value if isinstance(value, dict) else {}


def _safe_decimal(value):
    if value in (None, "", "null"):
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


def _related_inferences_for_recommendation(recommendation):
    scope_type = getattr(recommendation, "scope_type", None)
    scope_id = getattr(recommendation, "scope_id", None)

    if not scope_type or scope_id in (None, ""):
        return InferenceRecord.objects.none()

    if scope_type == "inference_record":
        return InferenceRecord.objects.filter(pk=scope_id).order_by("id")

    return InferenceRecord.objects.filter(
        source_type=scope_type,
        source_id=scope_id,
    ).order_by("id")


def _pick_company_name(recommendation):
    candidates = []

    for attr in ("company_name",):
        value = getattr(recommendation, attr, None)
        if value:
            candidates.append(value)

    rec_payload = _as_dict(getattr(recommendation, "payload", None))
    for key in ("company_name", "account_name", "organization", "company"):
        value = rec_payload.get(key)
        if value:
            candidates.append(value)

    for inf in _related_inferences_for_recommendation(recommendation):
        payload = _as_dict(getattr(inf, "inference_value", None))
        for key in ("company_name", "account_name", "organization", "company"):
            value = payload.get(key)
            if value:
                candidates.append(value)

    return next((value for value in candidates if value), "")


def _pick_confidence(recommendation):
    if getattr(recommendation, "confidence", None) is not None:
        return recommendation.confidence

    for inf in _related_inferences_for_recommendation(recommendation):
        confidence = getattr(inf, "confidence", None)
        if confidence is not None:
            return confidence

        payload = _as_dict(getattr(inf, "inference_value", None))
        for key in ("confidence", "score", "opportunity_confidence"):
            value = payload.get(key)
            if value is not None:
                return value

    return None


def _pick_estimated_value(recommendation):
    rec_payload = _as_dict(getattr(recommendation, "payload", None))
    for key in ("estimated_value", "amount", "budget", "price", "deal_value"):
        value = _safe_decimal(rec_payload.get(key))
        if value is not None:
            return value

    for inf in _related_inferences_for_recommendation(recommendation):
        payload = _as_dict(getattr(inf, "inference_value", None))
        for key in ("estimated_value", "amount", "budget", "price", "deal_value"):
            value = _safe_decimal(payload.get(key))
            if value is not None:
                return value

    return None


def _build_summary(recommendation):
    rec_text = (getattr(recommendation, "recommendation_text", None) or "").strip()
    related_inferences = list(_related_inferences_for_recommendation(recommendation)[:3])

    parts = []
    if rec_text:
        parts.append(rec_text)

    for inf in related_inferences:
        inf_type = getattr(inf, "inference_type", "") or ""
        payload = _as_dict(getattr(inf, "inference_value", None))

        signal = payload.get("commercial_signal")
        interest = payload.get("interest_level")
        snippet = None

        if signal:
            snippet = f"signal={signal}"
        elif interest:
            snippet = f"interest={interest}"
        elif inf_type:
            snippet = f"inference={inf_type}"

        if snippet:
            parts.append(snippet)

    if not parts:
        return "Opportunity creada desde recomendación IA."

    summary = " | ".join(parts)
    return summary[:1000]


def build_opportunity_defaults_from_recommendation(recommendation) -> dict:
    return {
        "company_name": _pick_company_name(recommendation),
        "confidence": _pick_confidence(recommendation),
        "estimated_value": _pick_estimated_value(recommendation),
        "summary": _build_summary(recommendation),
    }
