from __future__ import annotations

from dataclasses import dataclass

from apps.providers.registry import (
    get_calendar_provider,
    get_llm_provider,
    get_mail_provider,
)
from apps.emailing.services.mail_provider_service import prepare_provider_draft


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


def prepare_mail_provider_context(
    *,
    subject: str,
    body: str,
    to: list[str],
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
    reply_to_message_id: str | None = None,
    thread_ref: str | None = None,
    account_key: str | None = None,
    metadata: dict | None = None,
) -> dict:
    return prepare_provider_draft(
        subject=subject,
        body_text=body,
        to=to,
        cc=cc or [],
        bcc=bcc or [],
        reply_to_message_id=reply_to_message_id,
        thread_ref=thread_ref,
        account_key=account_key,
        metadata=metadata or {},
    )
