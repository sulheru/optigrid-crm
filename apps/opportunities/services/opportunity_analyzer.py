from apps.opportunities.services.context_builder import build_opportunity_analysis_context
from apps.recommendations.models import AIRecommendation


def _read(context, *names, default=None):
    for name in names:
        if isinstance(context, dict) and name in context:
            return context[name]
        if hasattr(context, name):
            return getattr(context, name)
    return default


def _exists_recommendation(opportunity, rec_type):
    return AIRecommendation.objects.filter(
        scope_type="opportunity",
        scope_id=opportunity.id,
        recommendation_type=rec_type,
        status="active"
    ).exists()


def _create_recommendation(opportunity, rec_type, text, confidence=0.7):
    return AIRecommendation.objects.create(
        scope_type="opportunity",
        scope_id=opportunity.id,
        recommendation_type=rec_type,
        recommendation_text=text,
        confidence=confidence,
        status="active"
    )


def analyze_opportunity_core(opportunity):
    context = build_opportunity_analysis_context(opportunity)

    created = 0
    reused = 0

    # -------------------------------------------------
    # SIGNAL: timing (ej: "escríbeme en mayo")
    # -------------------------------------------------
    timing_inferences = _read(context, "inferences", default=[])

    has_timing = False
    for inf in timing_inferences:
        inf_type = getattr(inf, "inference_type", None) if not isinstance(inf, dict) else inf.get("inference_type")
        if inf_type == "next_best_action":
            has_timing = True
            break

    if has_timing:
        if _exists_recommendation(opportunity, "followup"):
            reused += 1
        else:
            _create_recommendation(
                opportunity,
                "followup",
                "Schedule follow-up based on customer timing signal.",
                0.8
            )
            created += 1

    # -------------------------------------------------
    # SIGNAL: no tasks abiertas → next_action
    # -------------------------------------------------
    open_tasks = _read(context, "open_tasks", default=0)

    if open_tasks == 0:
        if _exists_recommendation(opportunity, "next_action"):
            reused += 1
        else:
            _create_recommendation(
                opportunity,
                "next_action",
                "Define next concrete action for this opportunity.",
                0.75
            )
            created += 1

    # -------------------------------------------------
    # SIGNAL: riesgo (sin actividad + sin progreso)
    # -------------------------------------------------
    active_recs = _read(context, "active_recommendations", default=[])

    if open_tasks == 0 and len(active_recs) == 0:
        if _exists_recommendation(opportunity, "risk_flag"):
            reused += 1
        else:
            _create_recommendation(
                opportunity,
                "risk_flag",
                "Opportunity may be stalling. No activity detected.",
                0.7
            )
            created += 1

    return created, reused
