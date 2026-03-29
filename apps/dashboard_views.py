from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

from django.contrib import messages
from django.shortcuts import redirect, render


def _safe_import(path: str, name: str):
    try:
        module = __import__(path, fromlist=[name])
        return getattr(module, name)
    except Exception:
        return None


AIRecommendation = _safe_import("apps.recommendations.models", "AIRecommendation")
CRMTask = _safe_import("apps.tasks.models", "CRMTask")
Opportunity = _safe_import("apps.opportunities.models", "Opportunity")
ExternalActionIntent = _safe_import("apps.external_actions.models", "ExternalActionIntent")

approve_recommendation_to_intent = _safe_import(
    "apps.recommendations.services.action_loop",
    "approve_recommendation_to_intent",
)
dismiss_recommendation = _safe_import(
    "apps.recommendations.services.action_loop",
    "dismiss_recommendation",
)


@dataclass
class DashboardCard:
    id: int | None
    title: str
    status: str
    priority: str
    confidence: str
    scope: str
    summary: str
    rationale: str
    created_at: str
    recommendation_type: str
    detail_url: str
    can_approve: bool
    can_dismiss: bool


def _safe_count(model) -> int:
    try:
        if model is None:
            return 0
        return model.objects.count()
    except Exception:
        return 0


def _safe_recent(model, limit: int = 12) -> list[Any]:
    if model is None:
        return []
    try:
        qs = model.objects.all()
        field_names = {f.name for f in model._meta.get_fields()}

        if "created_at" in field_names:
            qs = qs.order_by("-created_at")
        elif "id" in field_names:
            qs = qs.order_by("-id")

        return list(qs[:limit])
    except Exception:
        return []


def _field_names(model) -> set[str]:
    try:
        return {field.name for field in model._meta.get_fields()}
    except Exception:
        return set()


def _display(obj: Any, field_name: str) -> str | None:
    display_method = getattr(obj, f"get_{field_name}_display", None)
    if callable(display_method):
        try:
            value = display_method()
            if value not in (None, ""):
                return str(value)
        except Exception:
            pass

    value = getattr(obj, field_name, None)
    if value not in (None, ""):
        return str(value)

    return None


def _pick(obj: Any, *names: str, default: str = "—") -> str:
    for name in names:
        value = getattr(obj, name, None)
        if value not in (None, ""):
            return str(value)
    return default


def _short(text: Any, limit: int = 180) -> str:
    if text in (None, ""):
        return "—"
    text = " ".join(str(text).split())
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def _format_datetime(value: Any) -> str:
    if not value:
        return "—"
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return value.strftime(fmt)
        except Exception:
            continue
    return str(value)


def _priority_label(obj: Any) -> str:
    value = _display(obj, "priority")
    if value and value != "—":
        return value

    score = getattr(obj, "score", None)
    if score not in (None, ""):
        return f"score {score}"

    return "—"


def _confidence_label(obj: Any) -> str:
    value = getattr(obj, "confidence", None)
    if value in (None, ""):
        return "—"
    try:
        numeric = float(value)
        if 0 <= numeric <= 1:
            return f"{numeric:.2f}"
        return f"{numeric:g}"
    except Exception:
        return str(value)


def _scope_label(obj: Any) -> str:
    scope_type = _pick(obj, "scope_type", default="—")
    scope_id = getattr(obj, "scope_id", None)
    if scope_type == "—" and scope_id in (None, ""):
        return "—"
    if scope_id in (None, ""):
        return scope_type
    return f"{scope_type}:{scope_id}"


def _title_for_recommendation(obj: Any) -> str:
    recommendation_type = _display(obj, "recommendation_type") or _display(obj, "type")
    if recommendation_type:
        return recommendation_type.replace("_", " ").strip().title()

    text = _pick(obj, "recommendation_text", "text", "title", default="Recommendation")
    return _short(text, 80)


def _summary_for_recommendation(obj: Any) -> str:
    text = _pick(obj, "recommendation_text", "text", "summary", "title", default="—")
    return _short(text, 180)


def _rationale_for_recommendation(obj: Any) -> str:
    text = _pick(obj, "rationale", "reason", default="—")
    return _short(text, 160)


def _detail_url_for_recommendation(obj: Any) -> str:
    rec_id = getattr(obj, "id", None)
    if rec_id in (None, ""):
        return "/recommendations/"
    return f"/recommendations/?highlight={quote(str(rec_id))}"


def _can_approve_recommendation(obj: Any) -> bool:
    status = (_display(obj, "status") or "").lower()
    return status not in {"dismissed", "archived", "rejected", "expired"}


def _can_dismiss_recommendation(obj: Any) -> bool:
    status = (_display(obj, "status") or "").lower()
    return status not in {"dismissed", "archived", "rejected", "expired"}


def _normalize_recommendation(obj: Any) -> DashboardCard:
    recommendation_type = _display(obj, "recommendation_type") or _display(obj, "type") or "—"
    status = _display(obj, "status") or "—"

    return DashboardCard(
        id=getattr(obj, "id", None),
        title=_title_for_recommendation(obj),
        status=status,
        priority=_priority_label(obj),
        confidence=_confidence_label(obj),
        scope=_scope_label(obj),
        summary=_summary_for_recommendation(obj),
        rationale=_rationale_for_recommendation(obj),
        created_at=_format_datetime(getattr(obj, "created_at", None)),
        recommendation_type=recommendation_type,
        detail_url=_detail_url_for_recommendation(obj),
        can_approve=_can_approve_recommendation(obj),
        can_dismiss=_can_dismiss_recommendation(obj),
    )


def _load_recommendation_or_none(recommendation_id: Any):
    if AIRecommendation is None:
        return None
    try:
        return AIRecommendation.objects.filter(pk=recommendation_id).first()
    except Exception:
        return None


def _handle_action_loop_post(request):
    action = request.POST.get("action")
    recommendation_id = request.POST.get("recommendation_id")
    recommendation = _load_recommendation_or_none(recommendation_id)

    if recommendation is None:
        messages.error(request, "No se encontró la recommendation seleccionada.")
        return redirect("/")

    if action == "approve":
        if not callable(approve_recommendation_to_intent):
            messages.error(request, "El servicio de action loop no está disponible.")
            return redirect("/")

        result = approve_recommendation_to_intent(recommendation, getattr(request, "user", None))
        if result.ok:
            messages.success(request, result.message)
        else:
            messages.error(request, result.message)
        return redirect("/")

    if action == "dismiss":
        if not callable(dismiss_recommendation):
            messages.error(request, "El servicio de dismiss no está disponible.")
            return redirect("/")

        result = dismiss_recommendation(recommendation)
        if result.ok:
            messages.success(request, result.message)
        else:
            messages.error(request, result.message)
        return redirect("/")

    messages.warning(request, "Acción no reconocida.")
    return redirect("/")


def dashboard_home_view(request):
    if request.method == "POST":
        return _handle_action_loop_post(request)

    recent_recommendations = _safe_recent(AIRecommendation, limit=12)
    cards = [_normalize_recommendation(item) for item in recent_recommendations]

    context = {
        "kpis": {
            "recommendations": _safe_count(AIRecommendation),
            "tasks": _safe_count(CRMTask),
            "opportunities": _safe_count(Opportunity),
            "intents": _safe_count(ExternalActionIntent),
        },
        "recommendation_cards": cards,
        "recommendation_total": len(cards),
        "dashboard_links": {
            "recommendations": "/recommendations/",
            "tasks": "/tasks/",
            "opportunities": "/opportunities/prioritized/",
            "admin_intents": "/admin/external_actions/externalactionintent/",
        },
    }

    return render(request, "dashboard/index.html", context)
