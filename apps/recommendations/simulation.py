from typing import Optional, Dict

from apps.recommendations.models import AIRecommendation


def simulate_alternative(
    candidate: AIRecommendation,
    current_nba: Optional[AIRecommendation],
) -> Dict:
    if not current_nba:
        return {
            "message": "No hay acción principal para comparar."
        }

    c_dec = float(getattr(candidate, "decision_quality_score", 0.0) or 0.0)
    n_dec = float(getattr(current_nba, "decision_quality_score", 0.0) or 0.0)

    c_urg = float(getattr(candidate, "urgency_score", 0.0) or 0.0)
    n_urg = float(getattr(current_nba, "urgency_score", 0.0) or 0.0)

    c_conf = float(getattr(candidate, "confidence", 0.0) or 0.0)
    n_conf = float(getattr(current_nba, "confidence", 0.0) or 0.0)

    c_act = float(getattr(candidate, "actionability_bonus", 0.0) or 0.0)
    n_act = float(getattr(current_nba, "actionability_bonus", 0.0) or 0.0)

    return {
        "delta_decision": round(c_dec - n_dec, 2),
        "delta_urgency": round(c_urg - n_urg, 2),
        "delta_confidence": round(c_conf - n_conf, 2),
        "delta_actionability": round(c_act - n_act, 2),
        "better_choice": c_dec > n_dec,
    }
