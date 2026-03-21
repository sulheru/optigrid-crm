# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/strategy/services/context_builder.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Iterable

from django.apps import apps


OPEN_TASK_STATUSES = {"open", "pending_approval", "scheduled", "in_progress", "blocked"}
CLOSED_OPPORTUNITY_STATUSES = {"won", "lost", "archived", "cancelled", "closed"}
ACTIVE_RECOMMENDATION_STATUSES = {"new", "active", "acknowledged", "converted_to_task", "materialized"}


@dataclass
class StrategyContext:
    executive_summary: dict[str, Any]
    prioritized_opportunities: list[dict[str, Any]]
    at_risk_opportunities: list[dict[str, Any]]
    opportunities_without_open_tasks: list[dict[str, Any]]
    recent_recommendations: list[dict[str, Any]]
    open_tasks: list[dict[str, Any]]

    def as_dict(self) -> dict[str, Any]:
        return {
            "executive_summary": self.executive_summary,
            "prioritized_opportunities": self.prioritized_opportunities,
            "at_risk_opportunities": self.at_risk_opportunities,
            "opportunities_without_open_tasks": self.opportunities_without_open_tasks,
            "recent_recommendations": self.recent_recommendations,
            "open_tasks": self.open_tasks,
        }


def build_strategy_context() -> StrategyContext:
    opportunity_model = _resolve_model(
        app_labels=["opportunities"],
        model_names=["Opportunity"],
    )
    task_model = _resolve_model(
        app_labels=["tasks"],
        model_names=["CRMTask", "Task"],
    )
    recommendation_model = _resolve_model(
        app_labels=["recommendations"],
        model_names=["Recommendation", "AIRecommendation"],
    )

    prioritized_opportunities = _build_prioritized_opportunities(opportunity_model)
    at_risk_opportunities = _build_at_risk_opportunities(opportunity_model)
    open_tasks = _build_open_tasks(task_model)
    opportunities_without_open_tasks = _build_opportunities_without_open_tasks(
        opportunity_model=opportunity_model,
        task_model=task_model,
        prioritized_opportunities=prioritized_opportunities,
    )
    recent_recommendations = _build_recent_recommendations(recommendation_model)

    executive_summary = {
        "prioritized_opportunities_count": len(prioritized_opportunities),
        "at_risk_opportunities_count": len(at_risk_opportunities),
        "opportunities_without_open_tasks_count": len(opportunities_without_open_tasks),
        "open_tasks_count": len(open_tasks),
        "recent_recommendations_count": len(recent_recommendations),
    }

    return StrategyContext(
        executive_summary=executive_summary,
        prioritized_opportunities=prioritized_opportunities,
        at_risk_opportunities=at_risk_opportunities,
        opportunities_without_open_tasks=opportunities_without_open_tasks,
        recent_recommendations=recent_recommendations,
        open_tasks=open_tasks,
    )


def _resolve_model(app_labels: Iterable[str], model_names: Iterable[str]) -> Any | None:
    for app_label in app_labels:
        for model_name in model_names:
            try:
                return apps.get_model(app_label, model_name)
            except LookupError:
                continue
    return None


def _safe_queryset(model: Any):
    if model is None:
        return None
    try:
        qs = model.objects.all()
        if _has_field(model, "updated_at"):
            return qs.order_by("-updated_at")
        if _has_field(model, "created_at"):
            return qs.order_by("-created_at")
        return qs.order_by("-id")
    except Exception:
        return None


def _has_field(model: Any, field_name: str) -> bool:
    try:
        model._meta.get_field(field_name)
        return True
    except Exception:
        return False


def _build_prioritized_opportunities(opportunity_model: Any) -> list[dict[str, Any]]:
    qs = _safe_queryset(opportunity_model)
    if qs is None:
        return []

    items = []
    for obj in qs[:80]:
        item = _serialize_opportunity(obj)
        if not _is_active_opportunity(item):
            continue
        items.append(item)

    items.sort(
        key=lambda x: (
            _priority_rank(x.get("priority")),
            -(x.get("score") or 0),
            x.get("title") or "",
        )
    )
    return items[:7]


def _build_at_risk_opportunities(opportunity_model: Any) -> list[dict[str, Any]]:
    qs = _safe_queryset(opportunity_model)
    if qs is None:
        return []

    items = []
    for obj in qs[:80]:
        item = _serialize_opportunity(obj)
        if not _is_active_opportunity(item):
            continue
        if item["risk_flags"]:
            items.append(item)
        elif str(item.get("priority") or "").lower() == "monitor":
            items.append(item)

    return items[:7]


def _build_open_tasks(task_model: Any) -> list[dict[str, Any]]:
    qs = _safe_queryset(task_model)
    if qs is None:
        return []

    items = []
    for obj in qs[:100]:
        status = str(_first_attr(obj, "status", "task_status", default="") or "").lower()
        is_revoked = bool(_first_attr(obj, "is_revoked", default=False))
        if is_revoked:
            continue
        if status and status not in OPEN_TASK_STATUSES:
            continue
        items.append(_serialize_task(obj))

    return items[:10]


def _build_opportunities_without_open_tasks(
    opportunity_model: Any,
    task_model: Any,
    prioritized_opportunities: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    opportunity_ids_with_open_tasks = set()

    task_qs = _safe_queryset(task_model)
    if task_qs is not None:
        for task in task_qs[:200]:
            status = str(_first_attr(task, "status", "task_status", default="") or "").lower()
            is_revoked = bool(_first_attr(task, "is_revoked", default=False))
            if is_revoked:
                continue
            if status and status not in OPEN_TASK_STATUSES:
                continue
            opportunity_id = getattr(task, "opportunity_id", None)
            if opportunity_id is not None:
                opportunity_ids_with_open_tasks.add(opportunity_id)

    items = []
    seen = set()

    for item in prioritized_opportunities:
        item_id = item.get("id")
        if item_id is None or item_id in opportunity_ids_with_open_tasks:
            continue
        items.append(item)
        seen.add(item_id)

    qs = _safe_queryset(opportunity_model)
    if qs is not None:
        for obj in qs[:80]:
            item = _serialize_opportunity(obj)
            item_id = item.get("id")
            if item_id is None or item_id in seen:
                continue
            if not _is_active_opportunity(item):
                continue
            if item_id in opportunity_ids_with_open_tasks:
                continue
            items.append(item)
            seen.add(item_id)

    items.sort(
        key=lambda x: (
            _priority_rank(x.get("priority")),
            -(x.get("score") or 0),
        )
    )
    return items[:7]


def _build_recent_recommendations(recommendation_model: Any) -> list[dict[str, Any]]:
    qs = _safe_queryset(recommendation_model)
    if qs is None:
        return []

    items = []
    for obj in qs[:50]:
        status = str(_first_attr(obj, "status", default="") or "").lower()
        if status and status not in ACTIVE_RECOMMENDATION_STATUSES:
            continue
        items.append(_serialize_recommendation(obj))

    return items[:8]


def _serialize_opportunity(obj: Any) -> dict[str, Any]:
    return {
        "id": getattr(obj, "id", None),
        "title": _first_attr(obj, "title", "name", "opportunity_title", default=f"Opportunity {getattr(obj, 'id', '?')}"),
        "status": _first_attr(obj, "status", "opportunity_status", default=""),
        "priority": _first_attr(obj, "priority", default=""),
        "score": _coerce_number(_first_attr(obj, "score", default=0)),
        "summary": _first_attr(obj, "summary", default=""),
        "risk_flags": _normalize_list(_first_attr(obj, "risk_flags", default=[])),
        "next_actions": _normalize_list(_first_attr(obj, "next_actions", default=[])),
    }


def _serialize_task(obj: Any) -> dict[str, Any]:
    return {
        "id": getattr(obj, "id", None),
        "title": _first_attr(obj, "title", default=f"Task {getattr(obj, 'id', '?')}"),
        "status": _first_attr(obj, "status", "task_status", default=""),
        "due_at": _stringify(_first_attr(obj, "due_at", default="")),
        "source_action": _first_attr(obj, "source_action", default=""),
        "description": _first_attr(obj, "description", default=""),
        "opportunity_id": getattr(obj, "opportunity_id", None),
    }


def _serialize_recommendation(obj: Any) -> dict[str, Any]:
    return {
        "id": getattr(obj, "id", None),
        "type": _first_attr(obj, "recommendation_type", "type", default=""),
        "status": _first_attr(obj, "status", default=""),
        "priority": _first_attr(obj, "priority", default=""),
        "text": _first_attr(
            obj,
            "recommendation_text",
            "text",
            "title",
            "summary",
            default=f"Recommendation {getattr(obj, 'id', '?')}",
        ),
        "rationale": _first_attr(obj, "rationale", default=""),
    }


def _first_attr(obj: Any, *names: str, default: Any = None) -> Any:
    for name in names:
        if hasattr(obj, name):
            value = getattr(obj, name)
            if value is not None:
                return value
    return default


def _normalize_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    if isinstance(value, tuple):
        return [str(x).strip() for x in value if str(x).strip()]
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        if text.startswith("[") and text.endswith("]"):
            try:
                parsed = json.loads(text)
                if isinstance(parsed, list):
                    return [str(x).strip() for x in parsed if str(x).strip()]
            except Exception:
                pass
        if "|" in text:
            return [part.strip() for part in text.split("|") if part.strip()]
        if "," in text:
            return [part.strip() for part in text.split(",") if part.strip()]
        return [text]
    return [str(value).strip()]


def _coerce_number(value: Any) -> float:
    try:
        if value is None:
            return 0.0
        return float(value)
    except Exception:
        return 0.0


def _priority_rank(priority: Any) -> int:
    value = str(priority or "").strip().lower()
    if value == "high":
        return 0
    if value == "medium":
        return 1
    if value == "monitor":
        return 2
    if value == "low":
        return 3
    return 4


def _is_active_opportunity(item: dict[str, Any]) -> bool:
    status = str(item.get("status") or "").strip().lower()
    return status not in CLOSED_OPPORTUNITY_STATUSES


def _stringify(value: Any) -> str:
    if value in (None, ""):
        return ""
    return str(value)
