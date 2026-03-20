# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/strategy/services/prompt_builder.py
from __future__ import annotations

from typing import Any


def build_strategy_prompt(question: str, context: dict[str, Any]) -> str:
    executive = context.get("executive_summary", {})
    prioritized = context.get("prioritized_opportunities", [])
    at_risk = context.get("at_risk_opportunities", [])
    without_tasks = context.get("opportunities_without_open_tasks", [])
    recommendations = context.get("recent_recommendations", [])
    open_tasks = context.get("open_tasks", [])

    lines: list[str] = []

    lines.append("Eres Jarvis, asesor estratégico comercial de un CRM IA-first.")
    lines.append("Respondes al CEO con criterio ejecutivo, claridad y foco operativo.")
    lines.append("No inventes datos. Usa solo el contexto proporcionado.")
    lines.append("Prioriza ejecución, riesgo, foco y bloqueo comercial.")
    lines.append("")
    lines.append("Formato obligatorio de salida:")
    lines.append("PRIORIDADES")
    lines.append("- ...")
    lines.append("")
    lines.append("RIESGOS")
    lines.append("- ...")
    lines.append("")
    lines.append("ACCIONES RECOMENDADAS")
    lines.append("- ...")
    lines.append("")
    lines.append("Reglas:")
    lines.append("- Sé concreto.")
    lines.append("- Máximo 5 bullets por bloque.")
    lines.append("- Si falta información, dilo sin inventar.")
    lines.append("- Prioriza oportunidades high, score alto, riesgo y gaps de ejecución.")
    lines.append("- Trata como bloqueo importante una oportunidad sin task abierta.")
    lines.append("")
    lines.append("RESUMEN EJECUTIVO")
    for key, value in executive.items():
        lines.append(f"- {key}: {value}")
    lines.append("")

    lines.append("OPORTUNIDADES PRIORIZADAS")
    if prioritized:
        for item in prioritized[:7]:
            lines.append(_fmt_opportunity(item))
    else:
        lines.append("- Ninguna")

    lines.append("")
    lines.append("OPORTUNIDADES EN RIESGO")
    if at_risk:
        for item in at_risk[:7]:
            lines.append(_fmt_opportunity(item))
    else:
        lines.append("- Ninguna")

    lines.append("")
    lines.append("OPORTUNIDADES SIN TASK ABIERTA")
    if without_tasks:
        for item in without_tasks[:7]:
            lines.append(_fmt_opportunity(item))
    else:
        lines.append("- Ninguna")

    lines.append("")
    lines.append("TASKS ABIERTAS")
    if open_tasks:
        for item in open_tasks[:10]:
            lines.append(_fmt_task(item))
    else:
        lines.append("- Ninguna")

    lines.append("")
    lines.append("RECOMENDACIONES RECIENTES")
    if recommendations:
        for item in recommendations[:8]:
            lines.append(_fmt_recommendation(item))
    else:
        lines.append("- Ninguna")

    lines.append("")
    lines.append("PREGUNTA DEL CEO")
    lines.append(question.strip() or "¿Qué debo hacer ahora?")

    return "\n".join(lines).strip()


def _fmt_opportunity(item: dict[str, Any]) -> str:
    title = item.get("title") or f"Opportunity {item.get('id', '?')}"
    priority = item.get("priority") or "n/a"
    status = item.get("status") or "n/a"
    score = item.get("score") or 0
    risk_flags = ", ".join(item.get("risk_flags") or []) or "sin risk_flags"
    next_actions = ", ".join(item.get("next_actions") or []) or "sin next_actions"
    summary = item.get("summary") or ""
    company = item.get("company_name") or ""

    bits = [
        f"- {title}",
        f"priority={priority}",
        f"status={status}",
        f"score={score:.2f}",
    ]
    if company:
        bits.append(f"company={company}")
    bits.append(f"risk_flags={risk_flags}")
    bits.append(f"next_actions={next_actions}")
    if summary:
        bits.append(f"summary={summary}")
    return " | ".join(bits)


def _fmt_task(item: dict[str, Any]) -> str:
    title = item.get("title") or f"Task {item.get('id', '?')}"
    status = item.get("status") or "n/a"
    due_at = item.get("due_at") or "sin due"
    source_action = item.get("source_action") or "n/a"
    opportunity_id = item.get("opportunity_id") or "n/a"
    return (
        f"- {title} | status={status} | due_at={due_at} "
        f"| source_action={source_action} | opportunity_id={opportunity_id}"
    )


def _fmt_recommendation(item: dict[str, Any]) -> str:
    text = item.get("text") or f"Recommendation {item.get('id', '?')}"
    rec_type = item.get("type") or "n/a"
    status = item.get("status") or "n/a"
    priority = item.get("priority") or "n/a"
    rationale = item.get("rationale") or ""
    base = f"- {text} | type={rec_type} | status={status} | priority={priority}"
    if rationale:
        base += f" | rationale={rationale}"
    return base
