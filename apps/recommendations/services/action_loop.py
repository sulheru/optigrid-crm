from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ActionLoopResult:
    ok: bool
    message: str
    intent: Any | None = None


def _safe_import(path: str, name: str):
    try:
        module = __import__(path, fromlist=[name])
        return getattr(module, name)
    except Exception:
        return None


ExternalActionIntent = _safe_import("apps.external_actions.models", "ExternalActionIntent")


def _field_names(model) -> set[str]:
    try:
        return {field.name for field in model._meta.get_fields()}
    except Exception:
        return set()


def _get_choice_values(model, field_name: str) -> list[str]:
    try:
        field = model._meta.get_field(field_name)
        return [str(value) for value, _label in getattr(field, "choices", []) if value not in (None, "")]
    except Exception:
        return []


def _set_first_valid_choice(data: dict[str, Any], model, field_name: str, preferred: list[str]) -> None:
    if field_name in data:
        return
    choices = _get_choice_values(model, field_name)
    if not choices:
        return

    for candidate in preferred:
        if candidate in choices:
            data[field_name] = candidate
            return

    data[field_name] = choices[0]


def _recommendation_type(recommendation: Any) -> str:
    for field_name in ("recommendation_type", "type"):
        value = getattr(recommendation, field_name, None)
        if value not in (None, ""):
            return str(value)
    return "followup"


def _recommendation_text(recommendation: Any) -> str:
    for field_name in ("recommendation_text", "text", "title"):
        value = getattr(recommendation, field_name, None)
        if value not in (None, ""):
            return str(value)
    return "Recommendation"


def _recommendation_rationale(recommendation: Any) -> str:
    for field_name in ("rationale", "reason"):
        value = getattr(recommendation, field_name, None)
        if value not in (None, ""):
            return str(value)
    return ""


def _copy_scoping_fields(source: Any, data: dict[str, Any], model) -> None:
    model_fields = _field_names(model)
    for field_name in ("operating_organization", "mailbox_account"):
        if field_name in model_fields and hasattr(source, field_name):
            value = getattr(source, field_name, None)
            if value is not None:
                data[field_name] = value


def _existing_intent_for_recommendation(recommendation: Any) -> Any | None:
    if ExternalActionIntent is None:
        return None

    field_names = _field_names(ExternalActionIntent)
    relation_candidates = [
        "recommendation",
        "source_recommendation",
        "ai_recommendation",
    ]

    for relation_name in relation_candidates:
        if relation_name in field_names:
            try:
                return ExternalActionIntent.objects.filter(**{relation_name: recommendation}).order_by("-id").first()
            except Exception:
                continue

    return None


def dismiss_recommendation(recommendation: Any) -> ActionLoopResult:
    model = recommendation.__class__
    fields = _field_names(model)

    if "status" not in fields:
        return ActionLoopResult(
            ok=False,
            message="La recommendation no tiene campo status; no se puede hacer dismiss de forma segura.",
        )

    valid_statuses = _get_choice_values(model, "status")
    preferred = ["dismissed", "archived", "acknowledged"]

    target_status = None
    for candidate in preferred:
        if not valid_statuses or candidate in valid_statuses:
            target_status = candidate
            break

    if target_status is None:
        return ActionLoopResult(
            ok=False,
            message="No existe un estado compatible para dismiss en este modelo.",
        )

    setattr(recommendation, "status", target_status)
    recommendation.save(update_fields=["status"])
    return ActionLoopResult(ok=True, message=f"Recommendation marcada como {target_status}.")


def _try_service_materialization(recommendation: Any) -> Any | None:
    candidates = [
        ("apps.recommendations.services.external_actions", "create_external_action_intent_from_recommendation"),
        ("apps.recommendations.services.external_actions", "materialize_external_action_intent"),
        ("apps.recommendations.services.external_actions", "create_external_action_for_recommendation"),
        ("apps.recommendations.services.external_actions", "ensure_external_action_intent"),
        ("apps.recommendations.services.external_actions", "materialize_external_action"),
    ]

    for module_path, func_name in candidates:
        func = _safe_import(module_path, func_name)
        if not callable(func):
            continue

        try:
            intent = func(recommendation)
            if intent is not None:
                return intent
        except TypeError:
            try:
                intent = func(recommendation=recommendation)
                if intent is not None:
                    return intent
            except Exception:
                continue
        except Exception:
            continue

    return None


def _fallback_create_intent(recommendation: Any) -> Any | None:
    if ExternalActionIntent is None:
        return None

    model = ExternalActionIntent
    fields = _field_names(model)

    recommendation_type = _recommendation_type(recommendation)
    recommendation_text = _recommendation_text(recommendation)
    recommendation_rationale = _recommendation_rationale(recommendation)

    data: dict[str, Any] = {}
    _copy_scoping_fields(recommendation, data, model)

    if "intent_type" in fields:
        valid_types = _get_choice_values(model, "intent_type")
        if valid_types:
            if recommendation_type in valid_types:
                data["intent_type"] = recommendation_type
            elif "followup" in valid_types:
                data["intent_type"] = "followup"
            else:
                data["intent_type"] = valid_types[0]
        else:
            data["intent_type"] = recommendation_type

    relation_candidates = [
        "recommendation",
        "source_recommendation",
        "ai_recommendation",
    ]
    for relation_name in relation_candidates:
        if relation_name in fields:
            data[relation_name] = recommendation
            break

    if "provider" in fields:
        data["provider"] = "mail_stub"

    if "port_name" in fields:
        data["port_name"] = "email"

    if "adapter_key" in fields:
        data["adapter_key"] = "mail_stub"

    if "source_kind" in fields:
        data["source_kind"] = "recommendation"

    if "source_id" in fields:
        data["source_id"] = getattr(recommendation, "id", None)

    if "reason" in fields:
        data["reason"] = recommendation_text[:255]

    if "rationale" in fields:
        data["rationale"] = recommendation_rationale or recommendation_text

    if "payload" in fields:
        payload = {
            "action_loop": {
                "source": "dashboard",
                "recommendation_id": getattr(recommendation, "id", None),
                "recommendation_type": recommendation_type,
            },
            "message": {
                "subject": recommendation_text[:255],
                "body": recommendation_rationale or recommendation_text,
            },
        }
        if "mailbox_account" in data and data["mailbox_account"] is not None:
            payload["provider_context"] = {
                "account_key": getattr(data["mailbox_account"], "account_key", None),
                "mailbox_email": getattr(data["mailbox_account"], "email", None),
                "provider": getattr(data["mailbox_account"], "provider", None),
            }
        data["payload"] = payload

    if "normalized_preview" in fields:
        preview = {
            "provider": data.get("provider", "mail_stub"),
            "provider_status": "draft_only",
            "subject": recommendation_text[:255],
        }
        if "mailbox_account" in data and data["mailbox_account"] is not None:
            preview["account_key"] = getattr(data["mailbox_account"], "account_key", None)
            preview["mailbox_email"] = getattr(data["mailbox_account"], "email", None)
        if "operating_organization" in data and data["operating_organization"] is not None:
            preview["operating_organization"] = getattr(data["operating_organization"], "slug", None) or getattr(data["operating_organization"], "name", None)
        data["normalized_preview"] = preview

    _set_first_valid_choice(data, model, "approval_status", ["pending_approval", "pending", "approved"])
    _set_first_valid_choice(data, model, "dispatch_status", ["not_dispatched", "pending", "queued"])
    _set_first_valid_choice(data, model, "execution_status", ["draft", "not_executed", "pending"])

    try:
        return model.objects.create(**data)
    except Exception:
        return None


def _approve_intent_if_possible(intent: Any, user: Any) -> None:
    approve_fn = _safe_import("apps.external_actions.services.approval", "approve_external_action_intent")
    if callable(approve_fn):
        try:
            approve_fn(intent, user)
            return
        except Exception:
            pass

    model = intent.__class__
    fields = _field_names(model)

    updated_fields: list[str] = []

    if "approval_status" in fields:
        valid_statuses = _get_choice_values(model, "approval_status")
        for candidate in ("approved", "pending_approval", "pending"):
            if not valid_statuses or candidate in valid_statuses:
                setattr(intent, "approval_status", candidate)
                updated_fields.append("approval_status")
                break

    if "approved_by" in fields and user is not None:
        setattr(intent, "approved_by", user)
        updated_fields.append("approved_by")

    if updated_fields:
        try:
            intent.save(update_fields=updated_fields)
        except Exception:
            try:
                intent.save()
            except Exception:
                pass


def approve_recommendation_to_intent(recommendation: Any, user: Any = None) -> ActionLoopResult:
    existing = _existing_intent_for_recommendation(recommendation)
    if existing is not None:
        _approve_intent_if_possible(existing, user)
        return ActionLoopResult(
            ok=True,
            message=f"Ya existía un ExternalActionIntent #{getattr(existing, 'id', '—')} y quedó aprobado/preparado.",
            intent=existing,
        )

    intent = _try_service_materialization(recommendation)
    if intent is None:
        intent = _fallback_create_intent(recommendation)

    if intent is None:
        return ActionLoopResult(
            ok=False,
            message="No se pudo materializar un ExternalActionIntent para esta recommendation.",
        )

    _approve_intent_if_possible(intent, user)

    model = recommendation.__class__
    fields = _field_names(model)
    if "status" in fields:
        valid_statuses = _get_choice_values(model, "status")
        for candidate in ("acknowledged", "converted_to_task", "active"):
            if not valid_statuses or candidate in valid_statuses:
                try:
                    setattr(recommendation, "status", candidate)
                    recommendation.save(update_fields=["status"])
                except Exception:
                    pass
                break

    return ActionLoopResult(
        ok=True,
        message=f"ExternalActionIntent #{getattr(intent, 'id', '—')} creado y aprobado/preparado.",
        intent=intent,
    )
