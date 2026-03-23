from __future__ import annotations

from datetime import timedelta
from typing import Iterable, List, Optional, Tuple

from django.utils import timezone

from apps.core.ui_semantics import build_available_actions
from apps.emailing.models import InboundEmail
from apps.opportunities.models import Opportunity
from apps.recommendations.models import AIRecommendation
from apps.recommendations.priority import compute_priority_score


MIN_CONFIDENCE_FOR_NBA = 0.35

TYPE_WEIGHTS = {
    "reply_strategy": 100,
    "followup": 85,
    "contact_strategy": 72,
    "opportunity_review": 60,
}

PASSIVE_TEXT_PATTERNS = [
    "no insistir",
    "retomar",
    "más adelante",
    "mas adelante",
    "esperar",
    "wait",
    "later",
    "hold",
    "defer",
]


def _normalized_text(value) -> str:
    return (value or "").strip().lower()


def _clamp(value: float, min_value: float = 0.0, max_value: float = 100.0) -> float:
    return max(min_value, min(max_value, value))


def get_type_weight(recommendation: AIRecommendation) -> float:
    recommendation_type = _normalized_text(getattr(recommendation, "recommendation_type", ""))
    return float(TYPE_WEIGHTS.get(recommendation_type, 50))


def _resolve_opportunity_from_recommendation(
    recommendation: AIRecommendation,
) -> Optional[Opportunity]:
    direct_opportunity = getattr(recommendation, "opportunity", None)
    if direct_opportunity is not None:
        return direct_opportunity

    scope_type = _normalized_text(getattr(recommendation, "scope_type", ""))
    scope_id = getattr(recommendation, "scope_id", None)

    if scope_type != "opportunity" or scope_id in (None, ""):
        return None

    try:
        return Opportunity.objects.filter(pk=int(scope_id)).first()
    except (TypeError, ValueError):
        return None


def _get_latest_inbound_for_opportunity(
    opportunity: Optional[Opportunity],
) -> Optional[InboundEmail]:
    if opportunity is None:
        return None

    return (
        InboundEmail.objects.filter(opportunity=opportunity)
        .order_by("-received_at", "-created_at")
        .first()
    )


def _score_age_urgency(recommendation: AIRecommendation) -> Tuple[float, List[str]]:
    created_at = getattr(recommendation, "created_at", None)
    recommendation_type = _normalized_text(getattr(recommendation, "recommendation_type", ""))

    if created_at is None:
        return 0.0, []

    now = timezone.now()
    age = now - created_at

    flags: List[str] = []
    score = 0.0

    if recommendation_type == "reply_strategy":
        if age >= timedelta(days=4):
            score = 90
            flags.append("reply_overdue")
        elif age >= timedelta(days=2):
            score = 75
            flags.append("reply_delayed")
        elif age >= timedelta(days=1):
            score = 55
            flags.append("reply_pending_today")
        elif age >= timedelta(hours=4):
            score = 35
            flags.append("reply_recent_open")

    elif recommendation_type == "followup":
        if age >= timedelta(days=14):
            score = 90
            flags.append("followup_overdue")
        elif age >= timedelta(days=7):
            score = 75
            flags.append("followup_delayed")
        elif age >= timedelta(days=3):
            score = 55
            flags.append("followup_pending")
        elif age >= timedelta(days=1):
            score = 30
            flags.append("followup_recent")

    elif recommendation_type == "contact_strategy":
        if age >= timedelta(days=21):
            score = 70
            flags.append("contact_strategy_stale")
        elif age >= timedelta(days=7):
            score = 45
            flags.append("contact_strategy_pending")
        elif age >= timedelta(days=3):
            score = 20
            flags.append("contact_strategy_recent")

    elif recommendation_type == "opportunity_review":
        if age >= timedelta(days=14):
            score = 65
            flags.append("opportunity_review_stale")
        elif age >= timedelta(days=7):
            score = 40
            flags.append("opportunity_review_pending")
        elif age >= timedelta(days=2):
            score = 20
            flags.append("opportunity_review_recent")

    else:
        if age >= timedelta(days=14):
            score = 50
            flags.append("aging_recommendation")
        elif age >= timedelta(days=7):
            score = 30
            flags.append("pending_recommendation")

    return score, flags


def _score_conversation_urgency(
    recommendation: AIRecommendation,
) -> Tuple[float, List[str]]:
    recommendation_type = _normalized_text(getattr(recommendation, "recommendation_type", ""))
    opportunity = _resolve_opportunity_from_recommendation(recommendation)
    latest_inbound = _get_latest_inbound_for_opportunity(opportunity)

    if latest_inbound is None:
        return 0.0, []

    received_at = getattr(latest_inbound, "received_at", None) or getattr(
        latest_inbound, "created_at", None
    )
    if received_at is None:
        return 0.0, []

    now = timezone.now()
    age = now - received_at
    flags: List[str] = []

    if recommendation_type == "reply_strategy":
        if age <= timedelta(hours=24):
            flags.append("active_reply_window")
            return 35.0, flags
        if age <= timedelta(days=3):
            flags.append("warm_reply_window")
            return 25.0, flags
        if age <= timedelta(days=7):
            flags.append("cooling_reply_window")
            return 10.0, flags
        return 0.0, []

    if recommendation_type == "followup":
        if age <= timedelta(days=3):
            flags.append("recent_conversation_followup")
            return 20.0, flags
        if age <= timedelta(days=7):
            flags.append("warm_followup_window")
            return 12.0, flags
        return 0.0, []

    if recommendation_type == "opportunity_review":
        if age <= timedelta(days=7):
            flags.append("recent_signal_activity")
            return 10.0, flags

    return 0.0, []


def _score_scope_urgency(recommendation: AIRecommendation) -> Tuple[float, List[str]]:
    scope_type = _normalized_text(getattr(recommendation, "scope_type", ""))

    if scope_type == "opportunity":
        return 10.0, ["opportunity_scoped"]

    return 0.0, []


def compute_urgency_score(recommendation: AIRecommendation) -> float:
    age_score, _ = _score_age_urgency(recommendation)
    conversation_score, _ = _score_conversation_urgency(recommendation)
    scope_score, _ = _score_scope_urgency(recommendation)

    urgency_score = (0.60 * age_score) + (0.30 * conversation_score) + (0.10 * scope_score)
    return round(_clamp(urgency_score), 2)


def get_urgency_flags(recommendation: AIRecommendation) -> List[str]:
    flags: List[str] = []

    _, age_flags = _score_age_urgency(recommendation)
    _, conversation_flags = _score_conversation_urgency(recommendation)
    _, scope_flags = _score_scope_urgency(recommendation)

    for flag in age_flags + conversation_flags + scope_flags:
        if flag not in flags:
            flags.append(flag)

    return flags


def get_urgency_level(urgency_score: float) -> str:
    if urgency_score >= 70:
        return "high"
    if urgency_score >= 40:
        return "medium"
    return "low"


def compute_global_score(recommendation: AIRecommendation) -> float:
    priority_score = float(getattr(recommendation, "priority_score", 0.0) or 0.0)
    urgency_score = float(getattr(recommendation, "urgency_score", 0.0) or 0.0)
    type_weight = float(getattr(recommendation, "type_weight", 0.0) or 0.0)

    global_score = (
        (0.60 * priority_score)
        + (0.25 * urgency_score)
        + (0.15 * type_weight)
    )
    return round(_clamp(global_score), 2)


def _has_passive_text(recommendation: AIRecommendation) -> bool:
    text = _normalized_text(getattr(recommendation, "recommendation_text", ""))
    return any(pattern in text for pattern in PASSIVE_TEXT_PATTERNS)


def get_passive_penalty(recommendation: AIRecommendation) -> float:
    return 12.0 if _has_passive_text(recommendation) else 0.0


def get_actionability_bonus(recommendation: AIRecommendation) -> float:
    available_actions = getattr(recommendation, "available_actions", None)
    if available_actions is None:
        available_actions = build_available_actions(recommendation)
        recommendation.available_actions = available_actions

    if not available_actions:
        return 0.0

    labels = " ".join(_normalized_text(a.get("label", "")) for a in available_actions)
    bonus = 0.0

    if "execute" in labels:
        bonus += 10.0
    if "create task" in labels:
        bonus += 4.0

    return bonus


def classify_action_kind(recommendation: AIRecommendation) -> str:
    available_actions = getattr(recommendation, "available_actions", None)
    if available_actions is None:
        available_actions = build_available_actions(recommendation)
        recommendation.available_actions = available_actions

    if not available_actions:
        return "insight"

    if _has_passive_text(recommendation):
        return "insight"

    return "action"


def compute_decision_quality_score(recommendation: AIRecommendation) -> float:
    global_score = float(getattr(recommendation, "global_score", 0.0) or 0.0)
    passive_penalty = float(getattr(recommendation, "passive_penalty", 0.0) or 0.0)
    actionability_bonus = float(getattr(recommendation, "actionability_bonus", 0.0) or 0.0)

    score = global_score + actionability_bonus - passive_penalty
    return round(_clamp(score), 2)


def build_decision_summary(recommendation: AIRecommendation) -> str:
    if getattr(recommendation, "action_kind", "") == "insight":
        return "Insight only"

    urgency_level = getattr(recommendation, "urgency_level", "low")
    if urgency_level == "high":
        return "Act now"
    if urgency_level == "medium":
        return "Should be handled soon"
    return "Action available"


def build_decision_explanation(recommendation: AIRecommendation) -> str:
    parts: List[str] = []

    if getattr(recommendation, "action_kind", "") == "insight":
        parts.append("Se mantiene como insight")

        if getattr(recommendation, "passive_penalty", 0) > 0:
            parts.append("ya que el contenido sugiere esperar en lugar de actuar ahora")

        flags = getattr(recommendation, "urgency_flags", [])
        if flags:
            readable_flags = ", ".join(flag.replace("_", " ") for flag in flags[:2])
            parts.append(f"aunque sigue siendo relevante por señales como {readable_flags}")

        return ". ".join(parts) + "."

    urgency = getattr(recommendation, "urgency_level", "")

    if urgency == "high":
        parts.append("Seleccionada por alta urgencia")
    elif urgency == "medium":
        parts.append("Seleccionada por una combinación de urgencia y ejecutabilidad")
    else:
        parts.append("Seleccionada por ser una acción disponible")

    if getattr(recommendation, "actionability_bonus", 0) >= 10:
        parts.append("es directamente ejecutable desde el cockpit")

    flags = getattr(recommendation, "urgency_flags", [])
    if flags:
        readable_flags = ", ".join(flag.replace("_", " ") for flag in flags[:2])
        parts.append(f"presenta señales como {readable_flags}")

    return ". ".join(parts) + "."


def _why_not_selected(candidate: AIRecommendation, winner: AIRecommendation) -> str:
    if getattr(candidate, "action_kind", "") == "insight":
        return "Quedó fuera como acción principal porque se clasificó como insight."

    reasons: List[str] = []

    candidate_decision = float(getattr(candidate, "decision_quality_score", 0.0) or 0.0)
    winner_decision = float(getattr(winner, "decision_quality_score", 0.0) or 0.0)

    candidate_urgency = float(getattr(candidate, "urgency_score", 0.0) or 0.0)
    winner_urgency = float(getattr(winner, "urgency_score", 0.0) or 0.0)

    candidate_global = float(getattr(candidate, "global_score", 0.0) or 0.0)
    winner_global = float(getattr(winner, "global_score", 0.0) or 0.0)

    candidate_conf = float(getattr(candidate, "confidence", 0.0) or 0.0)
    winner_conf = float(getattr(winner, "confidence", 0.0) or 0.0)

    if candidate_decision < winner_decision:
        reasons.append("tiene menor decision score que la acción seleccionada")

    if candidate_urgency < winner_urgency:
        reasons.append("presenta menos urgencia")

    if candidate_global < winner_global:
        reasons.append("su score operativo es inferior")

    if candidate_conf < winner_conf:
        reasons.append("su confianza es más baja")

    if getattr(candidate, "actionability_bonus", 0) < getattr(winner, "actionability_bonus", 0):
        reasons.append("ofrece menor ejecutabilidad directa")

    if not reasons:
        reasons.append("quedó por detrás en el desempate del ranking")

    text = "; ".join(reasons[:2])
    return text[:1].upper() + text[1:] + "."


def annotate_competitive_reasons(recommendations: List[AIRecommendation]) -> List[AIRecommendation]:
    winner = get_next_best_action(recommendations)

    for recommendation in recommendations:
        if winner is not None and getattr(recommendation, "id", None) == getattr(winner, "id", None):
            recommendation.why_selected = recommendation.decision_explanation
            recommendation.why_not_selected = ""
        elif winner is not None:
            recommendation.why_selected = ""
            recommendation.why_not_selected = _why_not_selected(recommendation, winner)
        else:
            recommendation.why_selected = ""
            recommendation.why_not_selected = "No hay una acción principal seleccionada en este momento."

    return recommendations


def enrich_recommendation_scores(recommendation: AIRecommendation) -> AIRecommendation:
    recommendation.available_actions = build_available_actions(recommendation)
    recommendation.priority_score = round(float(compute_priority_score(recommendation) or 0.0), 2)
    recommendation.urgency_score = compute_urgency_score(recommendation)
    recommendation.urgency_flags = get_urgency_flags(recommendation)
    recommendation.urgency_level = get_urgency_level(recommendation.urgency_score)
    recommendation.type_weight = round(get_type_weight(recommendation), 2)
    recommendation.global_score = compute_global_score(recommendation)
    recommendation.passive_penalty = get_passive_penalty(recommendation)
    recommendation.actionability_bonus = get_actionability_bonus(recommendation)
    recommendation.decision_quality_score = compute_decision_quality_score(recommendation)
    recommendation.action_kind = classify_action_kind(recommendation)
    recommendation.decision_summary = build_decision_summary(recommendation)
    recommendation.decision_explanation = build_decision_explanation(recommendation)
    recommendation.why_selected = ""
    recommendation.why_not_selected = ""
    return recommendation


def _ranking_sort_key(recommendation: AIRecommendation):
    created_at = getattr(recommendation, "created_at", None) or timezone.make_aware(
        timezone.datetime.min
    )
    confidence = float(getattr(recommendation, "confidence", 0.0) or 0.0)

    return (
        float(getattr(recommendation, "global_score", 0.0) or 0.0),
        float(getattr(recommendation, "urgency_score", 0.0) or 0.0),
        float(getattr(recommendation, "priority_score", 0.0) or 0.0),
        confidence,
        -created_at.timestamp(),
        float(getattr(recommendation, "id", 0) or 0),
    )


def _nba_sort_key(recommendation: AIRecommendation):
    created_at = getattr(recommendation, "created_at", None) or timezone.make_aware(
        timezone.datetime.min
    )
    confidence = float(getattr(recommendation, "confidence", 0.0) or 0.0)

    return (
        float(getattr(recommendation, "decision_quality_score", 0.0) or 0.0),
        float(getattr(recommendation, "urgency_score", 0.0) or 0.0),
        float(getattr(recommendation, "global_score", 0.0) or 0.0),
        confidence,
        -created_at.timestamp(),
        float(getattr(recommendation, "id", 0) or 0),
    )


def rank_recommendations(
    recommendations: Iterable[AIRecommendation],
) -> List[AIRecommendation]:
    ranked = [enrich_recommendation_scores(rec) for rec in recommendations]
    ranked.sort(key=_ranking_sort_key, reverse=True)
    annotate_competitive_reasons(ranked)
    return ranked


def is_nba_eligible(recommendation: AIRecommendation) -> bool:
    if getattr(recommendation, "status", None) != AIRecommendation.STATUS_NEW:
        return False

    if getattr(recommendation, "action_kind", None) != "action":
        return False

    confidence = float(getattr(recommendation, "confidence", 0.0) or 0.0)
    if confidence < MIN_CONFIDENCE_FOR_NBA:
        return False

    return True


def get_next_best_action(
    recommendations: Iterable[AIRecommendation],
) -> Optional[AIRecommendation]:
    eligible = [rec for rec in recommendations if is_nba_eligible(rec)]
    if not eligible:
        return None

    eligible.sort(key=_nba_sort_key, reverse=True)
    return eligible[0]


def split_recommendations_by_kind(
    recommendations: Iterable[AIRecommendation],
) -> tuple[List[AIRecommendation], List[AIRecommendation]]:
    actionable = []
    insights = []

    for recommendation in recommendations:
        if getattr(recommendation, "action_kind", None) == "insight":
            insights.append(recommendation)
        else:
            actionable.append(recommendation)

    return actionable, insights
