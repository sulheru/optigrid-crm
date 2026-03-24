from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


from apps.recommendations.models import AIRecommendation


@dataclass(slots=True)
class MergeResult:
    kept: list[AIRecommendation]
    dismissed: list[AIRecommendation]


def _norm_source(value: str | None) -> str:
    value = (value or "").strip().lower()
    if value in {
        AIRecommendation.SOURCE_RULES,
        AIRecommendation.SOURCE_LLM,
        AIRecommendation.SOURCE_MERGED,
    }:
        return value
    return AIRecommendation.SOURCE_RULES


def _score(rec: AIRecommendation) -> tuple:
    return (
        float(getattr(rec, "confidence", 0) or 0),
        str(getattr(rec, "recommendation_text", "") or ""),
        str(getattr(rec, "scope_id", "") or ""),
    )


def _merge_text(rule_text: str | None, llm_text: str | None) -> str:
    rule_text = (rule_text or "").strip()
    llm_text = (llm_text or "").strip()

    if not rule_text:
        return llm_text
    if not llm_text:
        return rule_text

    if llm_text.lower() in rule_text.lower():
        return rule_text
    if rule_text.lower() in llm_text.lower():
        return llm_text

    return f"{rule_text}\n\nLLM enrichment:\n{llm_text}"


def merge_recommendation_candidates(
    recommendations: Iterable[AIRecommendation],
) -> MergeResult:
    grouped: dict[tuple[str, str, str], list[AIRecommendation]] = {}
    original: list[AIRecommendation] = []

    for rec in recommendations:
        if not getattr(rec, "source", None):
            rec.source = AIRecommendation.SOURCE_RULES
        key = (
            str(getattr(rec, "scope_type", "") or ""),
            str(getattr(rec, "scope_id", "") or ""),
            str(getattr(rec, "recommendation_type", "") or ""),
        )
        grouped.setdefault(key, []).append(rec)
        original.append(rec)

    kept: list[AIRecommendation] = []
    dismissed: list[AIRecommendation] = []

    for _, candidates in grouped.items():
        rules = [
            r for r in candidates
            if _norm_source(getattr(r, "source", None)) == AIRecommendation.SOURCE_RULES
        ]
        llm = [
            r for r in candidates
            if _norm_source(getattr(r, "source", None)) == AIRecommendation.SOURCE_LLM
        ]
        merged = [
            r for r in candidates
            if _norm_source(getattr(r, "source", None)) == AIRecommendation.SOURCE_MERGED
        ]

        if merged:
            winner = sorted(merged, key=_score, reverse=True)[0]
            kept.append(winner)
            dismissed.extend([r for r in candidates if r is not winner])
            continue

        if rules:
            rule_base = sorted(rules, key=_score, reverse=True)[0]

            if llm:
                llm_best = sorted(llm, key=_score, reverse=True)[0]
                merged_rec = AIRecommendation(
                    scope_type=rule_base.scope_type,
                    scope_id=rule_base.scope_id,
                    recommendation_type=rule_base.recommendation_type,
                    recommendation_text=_merge_text(
                        getattr(rule_base, "recommendation_text", ""),
                        getattr(llm_best, "recommendation_text", ""),
                    ),
                    confidence=max(
                        float(getattr(rule_base, "confidence", 0) or 0),
                        float(getattr(llm_best, "confidence", 0) or 0),
                    ),
                    status=getattr(rule_base, "status", AIRecommendation.STATUS_NEW),
                    source=AIRecommendation.SOURCE_MERGED,
                )
                kept.append(merged_rec)
                dismissed.extend(candidates)
            else:
                kept.append(rule_base)
                dismissed.extend([r for r in candidates if r is not rule_base])

            continue

        if llm:
            llm_best = sorted(llm, key=_score, reverse=True)[0]
            kept.append(llm_best)
            dismissed.extend([r for r in candidates if r is not llm_best])
            continue

        fallback = sorted(candidates, key=_score, reverse=True)[0]
        kept.append(fallback)
        dismissed.extend([r for r in candidates if r is not fallback])

    kept = sorted(kept, key=_score, reverse=True)
    return MergeResult(kept=kept, dismissed=dismissed)
