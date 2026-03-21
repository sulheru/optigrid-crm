# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/strategy/services/strategy_engine.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
from __future__ import annotations

from typing import Any

from .llm_backends import generate_strategy_answer


class StrategyEngine:
    """
    Fachada estable para la capa estratégica.
    V2 decide backend dinámicamente:
    - Gemini si está configurado
    - rule-based como fallback seguro
    """

    def answer(self, question: str, context: dict[str, Any]) -> str:
        result = generate_strategy_answer(question=question, context=context)
        return result.text
