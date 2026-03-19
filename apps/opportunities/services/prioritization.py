from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.utils import timezone

from apps.opportunities.models import Opportunity
from apps.opportunities.services.context_builder import build_opportunity_analysis_context
from apps.tasks.models import CRMTask


ACTION_LABELS = {
    "schedule_followup": "Schedule follow-up",
    "advance_opportunity": "Advance opportunity",
    "review_pricing_strategy": "Review pricing strategy",
    "review_opportunity_stall": "Review stalled opportunity",
    "define_next_action": "Define next action",
}

RISK_FLAG_LABELS = {
    "stale_interaction": "Stale interaction",
    "no_open_task": "No open task",
    "overdue_task": "Overdue task",
    "pricing_risk": "Pricing risk",
    "relationship_risk": "Relationship risk",
}

EXECUTION_STATUS_LABELS = {
    "blocked": "Blocked",
    "auto_task_open": "Auto task open",
    "task_open": "Task open",
    "suggested": "Suggested",
    "no_action": "No action",
}

PRIORITY_LABELS = {
    "high": "High",
    "medium": "Medium",
    "monitor": "Monitor",
    "low": "Low",
}


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _parse_dt(value: Any):
    if value is None:
        return None
    if hasattr(value, "isoformat"):
        return value
    if isinstance(value, str):
        try:
            from datetime import datetime
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except Exception:
            return None
    return None


def _latest_timestamp(items: list[dict], candidate_fields: list[str]):
    latest = None
    for item in items:
        for field in candidate_fields:
            dt = _parse_dt(item.get(field))
            if dt is None:
                continue
            if latest is None or dt > latest:
                latest = dt
    return latest


def _days_since(value):
    dt = _parse_dt(value)
    if dt is None:
        return None
    try:
        delta = timezone.now() - dt
        return max(delta.days, 0)
    except Exception:
        return None


def _contains_any(text: str, needles: list[str]) -> bool:
    haystack = _as_text(text).lower()
    return any(needle in haystack for needle in needles)


def _labelize(values: list[str], mapping: dict[str, str]) -> list[str]:
    return [mapping.get(v, v.replace("_", " ").title()) for v in values]


def _label(value: str, mapping: dict[str, str]) -> str:
    return mapping.get(value, value.replace("_", " ").title())


def _stage_base_score(stage: str) -> int:
    mapping = {
        "new": 35,
        "qualified": 65,
        "proposal": 75,
        "won": 100,
        "lost": 0,
    }
    return mapping.get(_as_text(stage).lower(), 40)


def _detect_interest_signal(context) -> bool:
    for fact in context.facts:
        fact_type = _as_text(fact.get("fact_type")).lower()
        if fact_type in {
            "interest_statement",
            "scope_statement",
            "budget_statement",
            "approval_statement",
            "scheduling_statement",
        }:
            return True

    for inf in context.inferences:
        inf_type = _as_text(inf.get("inference_type")).lower()
        inf_value = _as_text(inf.get("inference_value")).lower()
        if inf_type in {"interest_level", "opportunity_probability", "urgency_level"}:
            return True
        if _contains_any(inf_value, ["high", "medium", "qualified", "positive", "urgent"]):
            return True

    return False


def _detect_timing_signal(context) -> bool:
    for inf in context.inferences:
        inf_type = _as_text(inf.get("inference_type")).lower()
        inf_value = _as_text(inf.get("inference_value")).lower()
        rationale = _as_text(inf.get("rationale")).lower()

        if inf_type == "next_best_action":
            return True
        if _contains_any(inf_value, ["follow", "later", "next month", "may", "mayo"]):
            return True
        if _contains_any(rationale, ["timing", "follow-up", "follow up"]):
            return True

    for fact in context.facts:
        fact_type = _as_text(fact.get("fact_type")).lower()
        fact_value = _as_text(fact.get("fact_value")).lower()
        if fact_type == "timing_statement":
            return True
        if _contains_any(fact_value, ["follow up", "follow-up", "later", "next month", "may", "mayo"]):
            return True

    return False


def _detect_pricing_risk(context) -> bool:
    for fact in context.facts:
        fact_type = _as_text(fact.get("fact_type")).lower()
        fact_value = _as_text(fact.get("fact_value")).lower()
        if fact_type in {"objection_statement", "budget_statement"}:
            return True
        if _contains_any(fact_value, ["price", "pricing", "budget", "cost", "too expensive"]):
            return True

    for inf in context.inferences:
        inf_type = _as_text(inf.get("inference_type")).lower()
        inf_value = _as_text(inf.get("inference_value")).lower()
        if inf_type == "pricing_objection":
            return True
        if _contains_any(inf_value, ["pricing objection", "budget risk", "too expensive"]):
            return True

    return False


def _detect_relationship_risk(context) -> bool:
    for inf in context.inferences:
        inf_type = _as_text(inf.get("inference_type")).lower()
        inf_value = _as_text(inf.get("inference_value")).lower()
        rationale = _as_text(inf.get("rationale")).lower()

        if inf_type in {"risk_signal", "relationship_temperature"}:
            if _contains_any(inf_value, ["cold", "low", "negative", "risk"]):
                return True
            if _contains_any(rationale, ["stall", "stale", "blocked", "risk"]):
                return True

    return False


def _serialize_task(task: CRMTask) -> dict[str, Any]:
    return {
        "id": task.id,
        "title": task.title,
        "task_type": task.task_type,
        "status": task.status,
        "priority": getattr(task, "priority", None),
        "source": task.source,
        "source_action": task.source_action,
        "due_at": task.due_at.isoformat() if task.due_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None,
    }


def _load_task_rows(opportunity: Opportunity) -> dict[str, Any]:
    open_qs = CRMTask.objects.filter(
        opportunity=opportunity,
        status__in=["open", "in_progress"],
    ).order_by("due_at", "id")

    open_tasks = list(open_qs)
    auto_tasks = [task for task in open_tasks if _as_text(task.source).lower() == "auto"]

    overdue_task_count = 0
    now = timezone.now()
    for task in open_tasks:
        if task.due_at and task.due_at < now:
            overdue_task_count += 1

    return {
        "open_task_count": len(open_tasks),
        "overdue_task_count": overdue_task_count,
        "auto_task_count": len(auto_tasks),
        "open_tasks": [_serialize_task(task) for task in open_tasks],
        "auto_tasks": [_serialize_task(task) for task in auto_tasks],
    }


def _build_signals(context, opportunity: Opportunity) -> dict[str, Any]:
    latest_email_at = _latest_timestamp(context.emails, ["sent_at", "created_at"])
    days_since_last_interaction = _days_since(latest_email_at) if latest_email_at else None
    task_data = _load_task_rows(opportunity)

    return {
        "has_interest_signal": _detect_interest_signal(context),
        "has_timing_signal": _detect_timing_signal(context),
        "has_pricing_risk": _detect_pricing_risk(context),
        "has_relationship_risk": _detect_relationship_risk(context),
        "fact_count": len(context.facts),
        "inference_count": len(context.inferences),
        "email_count": len(context.emails),
        "open_task_count": task_data["open_task_count"],
        "overdue_task_count": task_data["overdue_task_count"],
        "auto_task_count": task_data["auto_task_count"],
        "active_recommendation_count": len(context.active_recommendations),
        "last_contact_at": latest_email_at.isoformat() if latest_email_at else None,
        "days_since_last_interaction": days_since_last_interaction,
        "open_tasks": task_data["open_tasks"],
        "auto_tasks": task_data["auto_tasks"],
    }


def _compute_score(context, signals: dict[str, Any]) -> int:
    score = _stage_base_score(context.opportunity.get("stage"))

    if signals["has_interest_signal"]:
        score += 15

    if signals["has_timing_signal"]:
        score += 10

    if signals["email_count"] > 0:
        score += 5

    if signals["fact_count"] >= 2:
        score += 5

    if signals["inference_count"] >= 2:
        score += 5

    if signals["days_since_last_interaction"] is not None:
        if signals["days_since_last_interaction"] <= 7:
            score += 10
        elif signals["days_since_last_interaction"] > 14:
            score -= 15

    if signals["open_task_count"] == 0:
        score -= 5

    if signals["overdue_task_count"] > 0:
        score -= 10

    if signals["has_pricing_risk"]:
        score -= 15

    if signals["has_relationship_risk"]:
        score -= 10

    return max(0, min(100, score))


def _priority_bucket(score: int) -> str:
    if score >= 80:
        return "high"
    if score >= 55:
        return "medium"
    if score >= 30:
        return "monitor"
    return "low"


def _build_risk_flags(signals: dict[str, Any]) -> list[str]:
    flags: list[str] = []

    if signals["days_since_last_interaction"] is not None and signals["days_since_last_interaction"] > 14:
        flags.append("stale_interaction")

    if signals["open_task_count"] == 0:
        flags.append("no_open_task")

    if signals["overdue_task_count"] > 0:
        flags.append("overdue_task")

    if signals["has_pricing_risk"]:
        flags.append("pricing_risk")

    if signals["has_relationship_risk"]:
        flags.append("relationship_risk")

    return flags


def _build_next_actions(signals: dict[str, Any], score: int) -> list[str]:
    actions: list[str] = []

    if signals["has_timing_signal"]:
        actions.append("schedule_followup")

    if signals["open_task_count"] == 0:
        actions.append("define_next_action")

    if signals["has_pricing_risk"]:
        actions.append("review_pricing_strategy")

    if signals["days_since_last_interaction"] is not None and signals["days_since_last_interaction"] > 14:
        actions.append("review_opportunity_stall")

    if score >= 70:
        actions.append("advance_opportunity")

    deduped: list[str] = []
    for action in actions:
        if action not in deduped:
            deduped.append(action)
    return deduped


def _build_execution_status(signals: dict[str, Any]) -> str:
    if signals["open_task_count"] > 0 and signals["overdue_task_count"] > 0:
        return "blocked"
    if signals["auto_task_count"] > 0:
        return "auto_task_open"
    if signals["open_task_count"] > 0:
        return "task_open"
    if signals["active_recommendation_count"] > 0:
        return "suggested"
    return "no_action"


@dataclass
class OpportunityPriorityRow:
    opportunity_id: int
    title: str
    company_name: str
    stage: str
    confidence: float
    estimated_value: Any
    relevance_score: int
    priority_bucket: str
    risk_flags: list[str]
    next_actions: list[str]
    open_task_count: int
    overdue_task_count: int
    auto_task_count: int
    active_recommendation_count: int
    execution_status: str
    last_contact_at: str | None
    days_since_last_interaction: int | None
    last_analyzed_at: str | None
    auto_tasks: list[dict[str, Any]]
    open_tasks: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "opportunity_id": self.opportunity_id,
            "title": self.title,
            "company_name": self.company_name,
            "stage": self.stage,
            "confidence": self.confidence,
            "estimated_value": self.estimated_value,
            "relevance_score": self.relevance_score,
            "priority_bucket": self.priority_bucket,
            "priority_label": _label(self.priority_bucket, PRIORITY_LABELS),
            "risk_flags": self.risk_flags,
            "risk_flag_labels": _labelize(self.risk_flags, RISK_FLAG_LABELS),
            "next_actions": self.next_actions,
            "next_action_labels": _labelize(self.next_actions, ACTION_LABELS),
            "open_task_count": self.open_task_count,
            "overdue_task_count": self.overdue_task_count,
            "auto_task_count": self.auto_task_count,
            "active_recommendation_count": self.active_recommendation_count,
            "execution_status": self.execution_status,
            "execution_status_label": _label(self.execution_status, EXECUTION_STATUS_LABELS),
            "last_contact_at": self.last_contact_at,
            "days_since_last_interaction": self.days_since_last_interaction,
            "last_analyzed_at": self.last_analyzed_at,
            "auto_tasks": self.auto_tasks,
            "open_tasks": self.open_tasks,
            "has_risk": len(self.risk_flags) > 0,
            "has_autotasks": self.auto_task_count > 0,
            "has_open_tasks": self.open_task_count > 0,
        }


def build_opportunity_priority_row(opportunity: Opportunity) -> OpportunityPriorityRow:
    context = build_opportunity_analysis_context(opportunity)
    signals = _build_signals(context, opportunity)
    score = _compute_score(context, signals)
    risk_flags = _build_risk_flags(signals)
    next_actions = _build_next_actions(signals, score)
    execution_status = _build_execution_status(signals)

    return OpportunityPriorityRow(
        opportunity_id=opportunity.id,
        title=_as_text(opportunity.title),
        company_name=_as_text(opportunity.company_name),
        stage=_as_text(opportunity.stage),
        confidence=float(opportunity.confidence or 0),
        estimated_value=opportunity.estimated_value,
        relevance_score=score,
        priority_bucket=_priority_bucket(score),
        risk_flags=risk_flags,
        next_actions=next_actions,
        open_task_count=signals["open_task_count"],
        overdue_task_count=signals["overdue_task_count"],
        auto_task_count=signals["auto_task_count"],
        active_recommendation_count=signals["active_recommendation_count"],
        execution_status=execution_status,
        last_contact_at=signals["last_contact_at"],
        days_since_last_interaction=signals["days_since_last_interaction"],
        last_analyzed_at=opportunity.last_analyzed_at.isoformat() if opportunity.last_analyzed_at else None,
        auto_tasks=signals["auto_tasks"],
        open_tasks=signals["open_tasks"],
    )


def build_prioritized_opportunities(*, stage: str | None = None, needs_attention_only: bool = False):
    queryset = Opportunity.objects.exclude(stage__in=["won", "lost"]).order_by("id")

    if stage:
        queryset = queryset.filter(stage=stage)

    rows: list[OpportunityPriorityRow] = []
    for opportunity in queryset:
        row = build_opportunity_priority_row(opportunity)

        if needs_attention_only:
            has_attention_signal = (
                row.priority_bucket in {"high", "medium"}
                or len(row.risk_flags) > 0
                or row.execution_status in {"blocked", "no_action"}
            )
            if not has_attention_signal:
                continue

        rows.append(row)

    rows.sort(
        key=lambda item: (
            item.relevance_score,
            len(item.risk_flags),
            item.opportunity_id,
        ),
        reverse=True,
    )
    return rows
