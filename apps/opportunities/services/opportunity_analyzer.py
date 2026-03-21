# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/opportunities/services/opportunity_analyzer.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.opportunities.services.autotasker import auto_materialize_tasks
from apps.opportunities.services.context_builder import build_opportunity_analysis_context
from apps.recommendations.models import AIRecommendation


ACTIVE_RECOMMENDATION_STATUSES = [
    AIRecommendation.STATUS_NEW,
    AIRecommendation.STATUS_MATERIALIZED,
]


@dataclass
class OpportunityAnalysisResult:
    opportunity_id: int
    analyzed: bool
    skipped_reason: str | None
    relevance_score: int
    priority_bucket: str
    risk_flags: list[str]
    next_actions: list[str]
    signals: dict[str, Any]
    recommendations_created: int
    recommendations_reused: int
    tasks_created: int
    tasks_reused: int
    analyzed_at: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "opportunity_id": self.opportunity_id,
            "analyzed": self.analyzed,
            "skipped_reason": self.skipped_reason,
            "relevance_score": self.relevance_score,
            "priority_bucket": self.priority_bucket,
            "risk_flags": self.risk_flags,
            "next_actions": self.next_actions,
            "signals": self.signals,
            "recommendations_created": self.recommendations_created,
            "recommendations_reused": self.recommendations_reused,
            "tasks_created": self.tasks_created,
            "tasks_reused": self.tasks_reused,
            "analyzed_at": self.analyzed_at,
        }


def _get_setting(name: str, default):
    return getattr(settings, name, default)


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
            return timezone.datetime.fromisoformat(value.replace("Z", "+00:00"))
        except Exception:
            return None
    return None


def _days_since(value: Any) -> int | None:
    dt = _parse_dt(value)
    if dt is None:
        return None
    now = timezone.now()
    try:
        delta = now - dt
    except Exception:
        return None
    return max(delta.days, 0)


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


def _normalize_text_blob(*parts: Any) -> str:
    text = " | ".join(_as_text(part).lower() for part in parts if _as_text(part))
    return " ".join(text.split())


def _recommendation_fingerprint(rec_type: str, text: str) -> str:
    return f"{rec_type}::{_normalize_text_blob(text)}"


def _active_recommendation_queryset(opportunity):
    return AIRecommendation.objects.filter(
        scope_type="opportunity",
        scope_id=str(opportunity.id),
        status__in=ACTIVE_RECOMMENDATION_STATUSES,
    )


def _existing_recommendation_by_fingerprint(opportunity, rec_type: str, text: str):
    target_fp = _recommendation_fingerprint(rec_type, text)
    for rec in _active_recommendation_queryset(opportunity):
        rec_fp = _recommendation_fingerprint(
            rec.recommendation_type,
            rec.recommendation_text,
        )
        if rec_fp == target_fp:
            return rec
    return None


def _create_or_reuse_recommendation(opportunity, rec_type: str, text: str, confidence: float):
    existing = _existing_recommendation_by_fingerprint(opportunity, rec_type, text)
    if existing is not None:
        return existing, False

    rec = AIRecommendation.objects.create(
        scope_type="opportunity",
        scope_id=str(opportunity.id),
        recommendation_type=rec_type,
        recommendation_text=text,
        confidence=confidence,
        status=AIRecommendation.STATUS_NEW,
    )
    return rec, True


def _infer_stage_base_score(stage: str) -> int:
    mapping = {
        "new": 35,
        "qualified": 65,
        "proposal": 75,
        "won": 100,
        "lost": 0,
    }
    return mapping.get(_as_text(stage).lower(), 40)


def _count_inference_types(inferences: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in inferences:
        key = _as_text(item.get("inference_type")).lower()
        if not key:
            continue
        counts[key] = counts.get(key, 0) + 1
    return counts


def _count_fact_types(facts: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in facts:
        key = _as_text(item.get("fact_type")).lower()
        if not key:
            continue
        counts[key] = counts.get(key, 0) + 1
    return counts


def _contains_any(text: str, needles: list[str]) -> bool:
    haystack = _as_text(text).lower()
    return any(needle in haystack for needle in needles)


def _detect_timing_signal(context) -> bool:
    for inf in context.inferences:
        inf_type = _as_text(inf.get("inference_type")).lower()
        inf_value = _as_text(inf.get("inference_value")).lower()
        rationale = _as_text(inf.get("rationale")).lower()

        if inf_type == "next_best_action":
            return True
        if "follow" in inf_value or "mayo" in inf_value or "later" in inf_value:
            return True
        if "timing" in rationale or "follow-up" in rationale or "follow up" in rationale:
            return True

    for fact in context.facts:
        fact_type = _as_text(fact.get("fact_type")).lower()
        fact_value = _as_text(fact.get("fact_value")).lower()
        if fact_type == "timing_statement":
            return True
        if _contains_any(fact_value, ["mayo", "next month", "later", "write me", "follow up"]):
            return True

    return False


def _detect_interest_signal(context) -> bool:
    for fact in context.facts:
        if _as_text(fact.get("fact_type")).lower() in {
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


def _build_signals(context) -> dict[str, Any]:
    latest_email_at = _latest_timestamp(context.emails, ["sent_at", "created_at"])
    latest_inference_at = _latest_timestamp(context.inferences, ["created_at"])
    latest_fact_at = _latest_timestamp(context.facts, ["observed_at", "created_at"])
    latest_task_at = _latest_timestamp(context.open_tasks, ["updated_at", "created_at"])

    days_since_last_interaction = None
    if latest_email_at is not None:
        days_since_last_interaction = _days_since(latest_email_at)

    overdue_tasks = 0
    now = timezone.now()
    for task in context.open_tasks:
        due_at = _parse_dt(task.get("due_at"))
        if due_at is not None and due_at < now:
            overdue_tasks += 1

    signal_map = {
        "inference_count": len(context.inferences),
        "fact_count": len(context.facts),
        "email_count": len(context.emails),
        "open_task_count": len(context.open_tasks),
        "active_recommendation_count": len(context.active_recommendations),
        "overdue_task_count": overdue_tasks,
        "days_since_last_interaction": days_since_last_interaction,
        "has_timing_signal": _detect_timing_signal(context),
        "has_interest_signal": _detect_interest_signal(context),
        "has_pricing_risk": _detect_pricing_risk(context),
        "has_relationship_risk": _detect_relationship_risk(context),
        "inference_type_counts": _count_inference_types(context.inferences),
        "fact_type_counts": _count_fact_types(context.facts),
        "latest_email_at": latest_email_at.isoformat() if latest_email_at else None,
        "latest_fact_at": latest_fact_at.isoformat() if latest_fact_at else None,
        "latest_inference_at": latest_inference_at.isoformat() if latest_inference_at else None,
        "latest_task_at": latest_task_at.isoformat() if latest_task_at else None,
    }
    return signal_map


def should_analyze(opportunity) -> tuple[bool, str | None]:
    if _as_text(opportunity.stage).lower() in {"won", "lost"}:
        return False, "closed_stage"

    min_recheck_hours = int(_get_setting("OPPORTUNITY_ANALYSIS_MIN_RECHECK_HOURS", 12) or 12)

    if opportunity.last_analyzed_at is None:
        return True, None

    threshold = timezone.now() - timedelta(hours=min_recheck_hours)

    if opportunity.updated_at and opportunity.updated_at >= opportunity.last_analyzed_at:
        return True, None

    if opportunity.last_analyzed_at <= threshold:
        return True, None

    return False, "freshly_analyzed"


def _compute_score(context, signals: dict[str, Any]) -> int:
    score = _infer_stage_base_score(context.opportunity.get("stage"))

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


def _build_next_actions(context, signals: dict[str, Any], risk_flags: list[str], score: int) -> list[str]:
    actions: list[str] = []

    if signals["has_timing_signal"]:
        actions.append("schedule_followup")

    if signals["open_task_count"] == 0:
        actions.append("define_next_action")

    if signals["has_pricing_risk"]:
        actions.append("review_pricing_strategy")

    if signals["days_since_last_interaction"] is not None and signals["days_since_last_interaction"] > 14:
        actions.append("review_opportunity_stall")

    if score >= 70 and "define_next_action" not in actions:
        actions.append("advance_opportunity")

    deduped: list[str] = []
    for item in actions:
        if item not in deduped:
            deduped.append(item)
    return deduped


def _materialize_recommendations(opportunity, signals, risk_flags, next_actions):
    created = 0
    reused = 0

    proposals: list[tuple[str, str, float]] = []

    if "schedule_followup" in next_actions:
        proposals.append((
            "followup",
            "Schedule follow-up based on customer timing signal.",
            0.80,
        ))

    if "define_next_action" in next_actions:
        proposals.append((
            "next_action",
            "Define next concrete action for this opportunity.",
            0.75,
        ))

    if "review_opportunity_stall" in next_actions:
        proposals.append((
            "opportunity_review",
            "Review this opportunity manually. Activity appears stale.",
            0.72,
        ))

    if "review_pricing_strategy" in next_actions:
        proposals.append((
            "pricing_strategy",
            "Review pricing approach before the next customer interaction.",
            0.74,
        ))

    if risk_flags and signals["open_task_count"] == 0:
        proposals.append((
            "hold",
            "Opportunity shows risk signals and no active execution path. Review before advancing.",
            0.70,
        ))

    for rec_type, text, confidence in proposals:
        _, was_created = _create_or_reuse_recommendation(
            opportunity=opportunity,
            rec_type=rec_type,
            text=text,
            confidence=confidence,
        )
        if was_created:
            created += 1
        else:
            reused += 1

    return created, reused


@transaction.atomic
def analyze_opportunity(opportunity, force: bool = False) -> OpportunityAnalysisResult:
    should_run, skipped_reason = should_analyze(opportunity)

    if force:
        should_run = True
        skipped_reason = None

    if not should_run:
        return OpportunityAnalysisResult(
            opportunity_id=opportunity.id,
            analyzed=False,
            skipped_reason=skipped_reason,
            relevance_score=0,
            priority_bucket="skipped",
            risk_flags=[],
            next_actions=[],
            signals={},
            recommendations_created=0,
            recommendations_reused=0,
            tasks_created=0,
            tasks_reused=0,
            analyzed_at=None,
        )

    context = build_opportunity_analysis_context(opportunity)
    signals = _build_signals(context)
    score = _compute_score(context, signals)
    risk_flags = _build_risk_flags(signals)
    next_actions = _build_next_actions(context, signals, risk_flags, score)
    priority_bucket = _priority_bucket(score)

    created, reused = _materialize_recommendations(
        opportunity=opportunity,
        signals=signals,
        risk_flags=risk_flags,
        next_actions=next_actions,
    )

    autotask = auto_materialize_tasks(
        opportunity=opportunity,
        priority_bucket=priority_bucket,
        next_actions=next_actions,
        risk_flags=risk_flags,
    )

    opportunity.last_analyzed_at = timezone.now()
    opportunity.save(update_fields=["last_analyzed_at", "updated_at"])

    return OpportunityAnalysisResult(
        opportunity_id=opportunity.id,
        analyzed=True,
        skipped_reason=None,
        relevance_score=score,
        priority_bucket=priority_bucket,
        risk_flags=risk_flags,
        next_actions=next_actions,
        signals=signals,
        recommendations_created=created,
        recommendations_reused=reused,
        tasks_created=autotask.created,
        tasks_reused=autotask.reused,
        analyzed_at=opportunity.last_analyzed_at.isoformat() if opportunity.last_analyzed_at else None,
    )


def analyze_opportunity_core(opportunity, force: bool = False):
    result = analyze_opportunity(opportunity=opportunity, force=force)
    return result.recommendations_created, result.recommendations_reused
