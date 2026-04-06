from __future__ import annotations

from typing import Any, List


def create_facts_from_email(email_message: Any) -> List[dict]:
    """
    No dependencia de EmailMessage model.
    Solo usa atributos genéricos.
    """
    facts = []

    subject = getattr(email_message, "subject", "") or ""
    body = getattr(email_message, "body", "") or ""

    if subject or body:
        facts.append({
            "type": "raw_email",
            "subject": subject,
            "body": body,
        })

    return facts
