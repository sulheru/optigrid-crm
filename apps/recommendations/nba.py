from dataclasses import dataclass
from typing import Iterable, List, Optional

from .models import AIRecommendation


@dataclass(frozen=True)
class ScoreBreakdown:
    priority_raw: float
    priority_component: float
    confidence_raw: float
    confidence_component: float
    urgency_raw: float
    urgency_component: float
    type_weight_raw: float
    type_weight_component: float
    total_score: float


@dataclass(frozen=True)
class NBACandidate:
    recommendation: AIRecommendation
    breakdown: ScoreBreakdown


@dataclass(frozen=True)
class NBAExplanation:
    recommendation: AIRecommendation
    breakdown: ScoreBreakdown
    why_selected: str
    why_not_others: List[str]
    alternatives: List["NBAAlternative"]


@dataclass(frozen=True)
class NBAAlternative:
    recommendation: AIRecommendation
    breakdown: ScoreBreakdown
    gap_vs_winner: float
    summary: str


PRIORITY_WEIGHT = 0.4
CONFIDENCE_WEIGHT = 0.2
URGENCY_WEIGHT = 0.3
TYPE_WEIGHT_WEIGHT = 0.1


def _as_float(value) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _priority_score(rec: AIRecommendation) -> float:
    return _as_float(getattr(rec, "priority_score", 0))


def _confidence_score(rec: AIRecommendation) -> float:
    return _as_float(getattr(rec, "confidence", 0))


def _urgency_score(rec: AIRecommendation) -> float:
    return _as_float(getattr(rec, "urgency_score", 0))


def _type_weight(rec: AIRecommendation) -> float:
    mapping = {
        "followup": 1.2,
        "reply_strategy": 1.1,
        "contact_strategy": 1.0,
        "opportunity_review": 1.3,
    }
    return _as_float(mapping.get(getattr(rec, "recommendation_type", None), 1.0))


def get_score_breakdown(rec: AIRecommendation) -> ScoreBreakdown:
    priority_raw = _priority_score(rec)
    confidence_raw = _confidence_score(rec)
    urgency_raw = _urgency_score(rec)
    type_weight_raw = _type_weight(rec)

    priority_component = priority_raw * PRIORITY_WEIGHT
    confidence_component = confidence_raw * CONFIDENCE_WEIGHT
    urgency_component = urgency_raw * URGENCY_WEIGHT
    type_weight_component = type_weight_raw * TYPE_WEIGHT_WEIGHT

    total_score = (
        priority_component
        + confidence_component
        + urgency_component
        + type_weight_component
    )

    return ScoreBreakdown(
        priority_raw=priority_raw,
        priority_component=priority_component,
        confidence_raw=confidence_raw,
        confidence_component=confidence_component,
        urgency_raw=urgency_raw,
        urgency_component=urgency_component,
        type_weight_raw=type_weight_raw,
        type_weight_component=type_weight_component,
        total_score=total_score,
    )


def compute_score(rec: AIRecommendation) -> float:
    return get_score_breakdown(rec).total_score


def build_candidates(recommendations: Iterable[AIRecommendation]) -> List[NBACandidate]:
    return [
        NBACandidate(recommendation=rec, breakdown=get_score_breakdown(rec))
        for rec in recommendations
    ]


def rank_candidates(recommendations: Iterable[AIRecommendation]) -> List[NBACandidate]:
    candidates = build_candidates(recommendations)
    return sorted(
        candidates,
        key=lambda candidate: (
            candidate.breakdown.total_score,
            candidate.breakdown.urgency_raw,
            candidate.breakdown.confidence_raw,
            candidate.recommendation.id,
        ),
        reverse=True,
    )


def select_best(candidates: List[NBACandidate]) -> Optional[AIRecommendation]:
    if not candidates:
        return None
    return rank_existing_candidates(candidates)[0].recommendation


def rank_existing_candidates(candidates: List[NBACandidate]) -> List[NBACandidate]:
    return sorted(
        candidates,
        key=lambda candidate: (
            candidate.breakdown.total_score,
            candidate.breakdown.urgency_raw,
            candidate.breakdown.confidence_raw,
            candidate.recommendation.id,
        ),
        reverse=True,
    )


def _compact_reason(candidate: NBACandidate) -> str:
    rec = candidate.recommendation
    b = candidate.breakdown
    rec_type = getattr(rec, "recommendation_type", "unknown")
    return (
        f"{rec_type}: total={b.total_score:.2f} "
        f"(priority={b.priority_component:.2f}, "
        f"confidence={b.confidence_component:.2f}, "
        f"urgency={b.urgency_component:.2f}, "
        f"type={b.type_weight_component:.2f})"
    )


def _why_selected_text(winner: NBACandidate) -> str:
    rec = winner.recommendation
    b = winner.breakdown
    rec_type = getattr(rec, "recommendation_type", "unknown")

    strongest_component_name = "priority"
    strongest_component_value = b.priority_component

    component_pairs = [
        ("confidence", b.confidence_component),
        ("urgency", b.urgency_component),
        ("type_weight", b.type_weight_component),
    ]
    for name, value in component_pairs:
        if value > strongest_component_value:
            strongest_component_name = name
            strongest_component_value = value

    return (
        f"Selected {rec_type} because it has the highest total score "
        f"({b.total_score:.2f}); strongest driver: {strongest_component_name} "
        f"({strongest_component_value:.2f})."
    )


def get_next_best_action(recommendations: Iterable[AIRecommendation]) -> Optional[AIRecommendation]:
    ranked = rank_candidates(recommendations)
    if not ranked:
        return None
    return ranked[0].recommendation


def get_next_best_action_explained(
    recommendations: Iterable[AIRecommendation],
    *,
    max_alternatives: int = 3,
) -> Optional[NBAExplanation]:
    ranked = rank_candidates(recommendations)
    if not ranked:
        return None

    winner = ranked[0]
    alternatives: List[NBAAlternative] = []
    why_not_others: List[str] = []

    for candidate in ranked[1 : 1 + max_alternatives]:
        gap = winner.breakdown.total_score - candidate.breakdown.total_score
        summary = (
            f"Not selected because it scored {gap:.2f} below the winner. "
            f"{_compact_reason(candidate)}"
        )
        alternatives.append(
            NBAAlternative(
                recommendation=candidate.recommendation,
                breakdown=candidate.breakdown,
                gap_vs_winner=gap,
                summary=summary,
            )
        )
        why_not_others.append(summary)

    return NBAExplanation(
        recommendation=winner.recommendation,
        breakdown=winner.breakdown,
        why_selected=_why_selected_text(winner),
        why_not_others=why_not_others,
        alternatives=alternatives,
    )
