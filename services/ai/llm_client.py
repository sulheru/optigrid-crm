# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/services/ai/llm_client.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
from __future__ import annotations

import json

from apps.providers.registry import get_llm_provider


class LLMClient:
    """
    Cliente estable de compatibilidad.

    Mantiene el contrato histórico del sistema:
    {
        "facts": [],
        "inferences": [],
        "proposals": [],
        "recommendations": [],
        "provider_meta": {...}
    }
    """

    def __init__(self, provider=None):
        self.provider = provider or get_llm_provider()

    def _default_result(self, raw_output: str) -> dict:
        return {
            "facts": [],
            "inferences": [],
            "proposals": [],
            "recommendations": [],
            "provider_meta": {
                "provider_class": self.provider.__class__.__name__,
                "raw_output": raw_output,
                "parsed": False,
            },
        }

    def _ensure_list(self, value):
        return value if isinstance(value, list) else []

    def _parse_structured_output(self, raw_output: str) -> dict:
        result = self._default_result(raw_output)

        try:
            payload = json.loads((raw_output or "").strip())
        except Exception:
            return result

        if not isinstance(payload, dict):
            return result

        result["facts"] = self._ensure_list(payload.get("facts"))
        result["inferences"] = self._ensure_list(payload.get("inferences"))
        result["proposals"] = self._ensure_list(payload.get("proposals"))
        result["recommendations"] = self._ensure_list(payload.get("recommendations"))
        result["provider_meta"]["parsed"] = True

        return result

    def analyze_email(self, email_text):
        raw_output = self.provider.infer(email_text)
        return self._parse_structured_output(raw_output)
