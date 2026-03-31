from typing import Any
from .models import FactRecord


def create_email_fact(email: Any) -> None:
    if email is None:
        return

    source_id = getattr(email, "id", None)

    FactRecord.objects.get_or_create(
        source_type="inbound_email",
        source_id=source_id,
        fact_type="email_received",
        defaults={
            "payload": {
                "subject": getattr(email, "subject", None),
            },
        },
    )
