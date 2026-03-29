from __future__ import annotations

from typing import Any


def send_email_draft(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "dispatch_status": "blocked",
        "reason": "email_send_guardrail_active",
        "provider_payload": payload,
    }
