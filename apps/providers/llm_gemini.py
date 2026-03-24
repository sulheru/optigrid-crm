from __future__ import annotations

import os

from .base import LLMProvider
from apps.strategy.services.llm_backends import generate_strategy_answer


INFERENCE_JSON_INSTRUCTIONS = """
Devuelve EXCLUSIVAMENTE un JSON válido, sin markdown, sin comentarios y sin texto adicional.

Formato exacto:
{
  "facts": [],
  "inferences": [
    {
      "type": "string",
      "confidence": 0.0,
      "value": {}
    }
  ],
  "proposals": [],
  "recommendations": [
    {
      "type": "followup|contact_strategy|reply_strategy|opportunity_review|pricing_strategy|advance_opportunity|mark_lost",
      "text": "string",
      "confidence": 0.0,
      "value": {}
    }
  ]
}

Reglas:
- Si no detectas nada útil, devuelve listas vacías.
- "confidence" debe ser float entre 0.0 y 1.0.
- "type" debe ser corto, estable y en snake_case.
- Para recommendations, SOLO se permiten estos tipos:
  - followup
  - contact_strategy
  - reply_strategy
  - opportunity_review
  - pricing_strategy
  - advance_opportunity
  - mark_lost
- "value" debe ser siempre un objeto JSON.
- "text" debe ser una recomendación breve y accionable.
- No inventes datos no soportados por el texto.
"""

CLASSIFICATION_JSON_INSTRUCTIONS = """
Devuelve EXCLUSIVAMENTE un JSON válido, sin markdown, sin comentarios y sin texto adicional.

Formato exacto:
{
  "label": "string",
  "confidence": 0.0
}

Reglas:
- "confidence" debe ser float entre 0.0 y 1.0.
- "label" debe ser corto y estable.
"""

GENERATION_JSON_INSTRUCTIONS = """
Devuelve EXCLUSIVAMENTE un JSON válido, sin markdown, sin comentarios y sin texto adicional.

Formato exacto:
{
  "text": "string"
}
"""


class GeminiLLMProvider(LLMProvider):
    def _run(self, prompt: str) -> str:
        previous = os.environ.get("STRATEGY_LLM_PROVIDER")
        os.environ["STRATEGY_LLM_PROVIDER"] = "gemini"
        try:
            result = generate_strategy_answer(question=prompt, context={})
            return result.text
        finally:
            if previous is None:
                os.environ.pop("STRATEGY_LLM_PROVIDER", None)
            else:
                os.environ["STRATEGY_LLM_PROVIDER"] = previous

    def _normalize_json_text(self, text: str) -> str:
        cleaned = (text or "").strip()

        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            if lines:
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()

        return cleaned

    def _run_json_prompt(self, instructions: str, user_text: str) -> str:
        prompt = f"{instructions}\n\nTexto de entrada:\n{user_text}\n"
        raw = self._run(prompt)
        return self._normalize_json_text(raw)

    def infer(self, prompt: str) -> str:
        return self._run_json_prompt(INFERENCE_JSON_INSTRUCTIONS, prompt)

    def classify(self, text: str) -> str:
        return self._run_json_prompt(CLASSIFICATION_JSON_INSTRUCTIONS, text)

    def generate(self, prompt: str) -> str:
        return self._run_json_prompt(GENERATION_JSON_INSTRUCTIONS, prompt)
