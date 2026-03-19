from __future__ import annotations

from typing import Any


class RuleBasedStrategyAdvisor:
    def answer(self, question: str, context: dict[str, Any]) -> str:
        q = (question or "").strip().lower()

        priorities = self._build_priorities(q, context)
        risks = self._build_risks(q, context)
        actions = self._build_actions(q, context)

        lines = ["PRIORIDADES"]
        lines.extend(f"- {item}" for item in priorities or ["No hay prioridades claras detectadas ahora mismo."])
        lines.append("")
        lines.append("RIESGOS")
        lines.extend(f"- {item}" for item in risks or ["No se detectan riesgos relevantes con la información disponible."])
        lines.append("")
        lines.append("ACCIONES RECOMENDADAS")
        lines.extend(f"- {item}" for item in actions or ["No hay acciones recomendadas inmediatas."])

        return "\n".join(lines).strip()

    def _build_priorities(self, q: str, context: dict[str, Any]) -> list[str]:
        items = []

        prioritized = context.get("prioritized_opportunities", [])
        without_tasks = context.get("opportunities_without_open_tasks", [])
        open_tasks = context.get("open_tasks", [])

        without_task_ids = {o.get("id") for o in without_tasks}

        for opp in prioritized:
            if str(opp.get("priority")).lower() == "high" and opp.get("id") in without_task_ids:
                items.append(f"{opp.get('title')}: HIGH sin ejecución activa → prioridad crítica")

        for opp in prioritized[:3]:
            title = opp.get("title")
            score = opp.get("score") or 0
            items.append(f"{title} · score {score:.2f}")

        if any(t in q for t in ["hoy", "today", "qué hago", "que hago"]):
            for task in open_tasks[:3]:
                items.insert(0, f"Ejecutar: {task['title']}")

        return self._dedupe(items)[:5]

    def _build_risks(self, q: str, context: dict[str, Any]) -> list[str]:
        items = []

        at_risk = context.get("at_risk_opportunities", [])
        without_tasks = context.get("opportunities_without_open_tasks", [])
        summary = context.get("executive_summary", {})

        for opp in at_risk[:4]:
            title = opp.get("title")
            flags = opp.get("risk_flags") or []
            if flags:
                items.append(f"{title}: {', '.join(flags[:2])}")
            else:
                items.append(f"{title}: en estado monitor (riesgo latente)")

        for opp in without_tasks[:4]:
            title = opp.get("title")
            items.append(f"{title}: sin ejecución → bloqueada")

        if summary.get("open_tasks_count", 0) > 15:
            items.append("Demasiadas tasks abiertas → dispersión operativa")

        if summary.get("open_tasks_count", 0) == 0 and summary.get("prioritized_opportunities_count", 0) > 0:
            items.append("Hay oportunidades pero ninguna ejecución → bloqueo total")

        return self._dedupe(items)[:5]

    def _build_actions(self, q: str, context: dict[str, Any]) -> list[str]:
        items = []

        prioritized = context.get("prioritized_opportunities", [])
        without_tasks = context.get("opportunities_without_open_tasks", [])
        recommendations = context.get("recent_recommendations", [])

        if without_tasks:
            items.append("Convertir oportunidades sin task en ejecución inmediata")

        items.append("Concentrar esfuerzo en oportunidades HIGH antes de abrir nuevas")

        for opp in prioritized[:2]:
            title = opp.get("title")
            next_actions = opp.get("next_actions") or []
            if next_actions:
                items.append(f"{title}: ejecutar → {next_actions[0]}")
            else:
                items.append(f"{title}: definir siguiente acción concreta")

        for rec in recommendations[:2]:
            text = rec.get("text")
            items.append(f"Evaluar: {text}")

        if "riesgo" in q or "bloqueo" in q:
            items.insert(0, "Resolver primero bloqueos antes de optimizar pipeline")

        if "potencial" in q or "focus" in q or "enfoc" in q:
            items.insert(0, "Invertir tiempo en oportunidades con mayor score")

        return self._dedupe(items)[:6]

    def _dedupe(self, items: list[str]) -> list[str]:
        seen = set()
        result = []
        for item in items:
            value = item.strip()
            if not value or value in seen:
                continue
            seen.add(value)
            result.append(value)
        return result
