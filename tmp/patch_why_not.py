def _why_not_selected(candidate, winner) -> str:
    if getattr(candidate, "action_kind", "") == "insight":
        return "Se clasificó como insight y no como acción ejecutable."

    reasons = []

    c_dec = float(getattr(candidate, "decision_quality_score", 0.0) or 0.0)
    w_dec = float(getattr(winner, "decision_quality_score", 0.0) or 0.0)

    c_urg = float(getattr(candidate, "urgency_score", 0.0) or 0.0)
    w_urg = float(getattr(winner, "urgency_score", 0.0) or 0.0)

    c_conf = float(getattr(candidate, "confidence", 0.0) or 0.0)
    w_conf = float(getattr(winner, "confidence", 0.0) or 0.0)

    c_act = float(getattr(candidate, "actionability_bonus", 0.0) or 0.0)
    w_act = float(getattr(winner, "actionability_bonus", 0.0) or 0.0)

    # Diferencias reales
    if c_dec < w_dec:
        reasons.append("menor impacto global en la decisión")

    if c_urg < w_urg:
        reasons.append("menor urgencia")

    if c_conf < w_conf:
        reasons.append("menor confianza")

    if c_act < w_act:
        reasons.append("menor facilidad de ejecución directa")

    # Caso empate real
    if not reasons:
        return "Tiene métricas similares, pero no aporta ventaja diferencial frente a la seleccionada."

    text = " y ".join(reasons[:2])
    return text[:1].upper() + text[1:] + "."
