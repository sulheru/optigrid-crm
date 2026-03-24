from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ExecutionAdapterRegistry:
    """
    Placeholder estable para la futura provider abstraction layer.

    Futuro:
    - MailProvider
    - CalendarProvider
    - LLMProvider
    - SimulationRouter
    """
    mail_provider: str = "embedded"
    calendar_provider: str = "none"
    llm_provider: str = "embedded"
    execution_mode: str = "local"


def get_execution_adapters() -> ExecutionAdapterRegistry:
    return ExecutionAdapterRegistry()
