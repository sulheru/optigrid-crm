from __future__ import annotations

from dataclasses import dataclass

from apps.providers.registry import (
    get_calendar_provider,
    get_llm_provider,
    get_mail_provider,
)


@dataclass
class ExecutionAdapterRegistry:
    """
    Registry estable para la provider abstraction layer.

    Expone instancias concretas resueltas desde settings sin obligar
    a la capa de ejecución a conocer implementaciones concretas.
    """
    mail_provider: object
    calendar_provider: object
    llm_provider: object
    execution_mode: str = "local"


def get_execution_adapters() -> ExecutionAdapterRegistry:
    return ExecutionAdapterRegistry(
        mail_provider=get_mail_provider(),
        calendar_provider=get_calendar_provider(),
        llm_provider=get_llm_provider(),
        execution_mode="local",
    )
