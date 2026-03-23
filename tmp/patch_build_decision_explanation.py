def build_decision_explanation(recommendation) -> str:
    parts = []

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
