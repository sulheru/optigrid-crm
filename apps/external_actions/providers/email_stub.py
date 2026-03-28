from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class EmailStubResult:
    ok: bool
    provider: str
    action: str
    provider_message_id: str
    simulated_at: str
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def send_email_draft(intent) -> dict[str, Any]:
    """
    Provider stub.
    NO envía ningún correo real.
    Solo simula ejecución satisfactoria y devuelve un resultado estructurado.
    """
    intent_pk = getattr(intent, "pk", None) or "unknown"

    result = EmailStubResult(
        ok=True,
        provider="email_stub",
        action="send_email_draft",
        provider_message_id=f"stub-email-{intent_pk}",
        simulated_at=datetime.utcnow().isoformat() + "Z",
        detail="Simulated outbound email dispatch. No real email was sent.",
    )
    return result.to_dict()
