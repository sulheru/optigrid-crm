from __future__ import annotations

from django.conf import settings

from .mail_embedded import EmbeddedMailProvider
from .llm_embedded import EmbeddedLLMProvider


def get_mail_provider():
    provider = getattr(settings, "MAIL_PROVIDER", "embedded")

    if provider == "embedded":
        return EmbeddedMailProvider()

    raise ValueError(f"Unknown MAIL_PROVIDER: {provider}")


def get_llm_provider():
    provider = getattr(settings, "LLM_PROVIDER", "embedded")

    if provider == "embedded":
        return EmbeddedLLMProvider()

    raise ValueError(f"Unknown LLM_PROVIDER: {provider}")
