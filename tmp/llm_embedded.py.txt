from __future__ import annotations

from .base import LLMProvider


class EmbeddedLLMProvider(LLMProvider):

    def infer(self, prompt: str) -> str:
        return "inference_stub"

    def classify(self, text: str) -> str:
        return "classification_stub"

    def generate(self, prompt: str) -> str:
        return "generation_stub"
