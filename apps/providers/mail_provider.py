from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(slots=True)
class MailAccountRef:
    provider: str
    account_key: str = "default"
    mailbox: str | None = None
    display_name: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class DraftEnvelope:
    subject: str
    body_text: str
    to: list[str]
    cc: list[str] = field(default_factory=list)
    bcc: list[str] = field(default_factory=list)
    reply_to_message_id: str | None = None
    thread_ref: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ProviderDraftResult:
    provider: str
    account_key: str
    external_draft_id: str | None
    status: str
    payload: dict[str, Any] = field(default_factory=dict)


class MailProvider(Protocol):
    provider_key: str

    def create_draft(
        self,
        *,
        account: MailAccountRef,
        envelope: DraftEnvelope,
    ) -> ProviderDraftResult:
        ...
