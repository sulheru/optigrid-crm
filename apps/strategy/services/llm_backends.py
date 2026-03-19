from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Protocol

from .prompt_builder import build_strategy_prompt


class StrategyBackend(Protocol):
    def generate(self, question: str, context: dict) -> str:
        ...


@dataclass
class BackendResult:
    text: str
    backend_name: str


class RuleBasedStrategyBackend:
    backend_name = "rule_based"

    def generate(self, question: str, context: dict) -> str:
        from .rule_based_engine import RuleBasedStrategyAdvisor
        advisor = RuleBasedStrategyAdvisor()
        return advisor.answer(question=question, context=context)


class GeminiStrategyBackend:
    backend_name = "gemini"

    def __init__(self, model: str | None = None):
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    def generate(self, question: str, context: dict) -> str:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY no está configurada")

        try:
            from google import genai
        except Exception as exc:
            raise RuntimeError(
                "No se pudo importar google.genai. Instala el paquete 'google-genai'."
            ) from exc

        prompt = build_strategy_prompt(question=question, context=context)

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        text = getattr(response, "text", None)
        if not text:
            raise RuntimeError("Gemini devolvió una respuesta vacía")

        return text.strip()


def get_strategy_backend() -> StrategyBackend:
    provider = (os.getenv("STRATEGY_LLM_PROVIDER") or "").strip().lower()

    if provider == "gemini":
        return GeminiStrategyBackend()

    return RuleBasedStrategyBackend()


def generate_strategy_answer(question: str, context: dict) -> BackendResult:
    backend = get_strategy_backend()

    try:
        text = backend.generate(question=question, context=context)
        return BackendResult(
            text=text,
            backend_name=getattr(backend, "backend_name", "unknown"),
        )
    except Exception:
        fallback = RuleBasedStrategyBackend()
        text = fallback.generate(question=question, context=context)
        return BackendResult(text=text, backend_name="rule_based_fallback")
