from __future__ import annotations

from apps.core.runtime_settings import get_runtime_str_setting

from .calendar_placeholder import PlaceholderCalendarProvider
from .llm_embedded import EmbeddedLLMProvider
from .llm_gemini import GeminiLLMProvider
from .mail_embedded import EmbeddedMailProvider
from .mail_m365 import M365MailProvider


def get_mail_provider_name() -> str:
    return get_runtime_str_setting("MAIL_PROVIDER", "embedded").strip().lower() or "embedded"


def get_llm_provider_name() -> str:
    return get_runtime_str_setting("LLM_PROVIDER", "embedded").strip().lower() or "embedded"


def get_mail_provider():
    provider = get_mail_provider_name()

    if provider == "embedded":
        return EmbeddedMailProvider()

    if provider == "m365":
        return M365MailProvider()

    raise ValueError(f"Unknown MAIL_PROVIDER: {provider}")


def get_llm_provider():
    provider = get_llm_provider_name()

    if provider == "embedded":
        return EmbeddedLLMProvider()

    if provider == "gemini":
        return GeminiLLMProvider()

    raise ValueError(f"Unknown LLM_PROVIDER: {provider}")


def get_calendar_provider():
    return PlaceholderCalendarProvider()
