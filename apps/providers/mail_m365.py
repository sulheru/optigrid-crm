from __future__ import annotations

from django.conf import settings

from .base import MailProvider
from services.m365.graph_client import GraphClient


class M365MailProvider(MailProvider):
    """
    Wrapper mínimo sobre GraphClient.

    No implementa envío real ni drafts reales todavía.
    Solo prepara la abstracción para la futura integración M365.
    """

    def __init__(self, access_token: str | None = None):
        token = access_token or getattr(settings, "M365_ACCESS_TOKEN", "")
        self.client = GraphClient(token) if token else None

    def create_draft(self, *, to: str, subject: str, body: str) -> dict:
        return {
            "provider": "m365",
            "status": "draft_not_implemented",
            "to": to,
            "subject": subject,
            "body": body,
        }

    def send_email(self, *, draft_id: str | None = None) -> dict:
        return {
            "provider": "m365",
            "status": "send_not_implemented",
            "draft_id": draft_id,
        }

    def fetch_inbox(self) -> list[dict]:
        if self.client is None:
            return []

        data = self.client.list_messages()
        if isinstance(data, dict):
            value = data.get("value")
            if isinstance(value, list):
                return value
        return []
