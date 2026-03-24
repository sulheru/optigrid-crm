from __future__ import annotations

from .base import MailProvider


class EmbeddedMailProvider(MailProvider):

    def create_draft(self, *, to: str, subject: str, body: str) -> dict:
        return {
            "provider": "embedded",
            "status": "draft_created",
            "to": to,
            "subject": subject,
        }

    def send_email(self, *, draft_id: str | None = None) -> dict:
        return {
            "provider": "embedded",
            "status": "sent",
            "draft_id": draft_id,
        }

    def fetch_inbox(self) -> list[dict]:
        return []
