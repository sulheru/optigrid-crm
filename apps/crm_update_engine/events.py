"""
CRM Update Engine — Internal Events (V0)

No persistente todavía.
Sirve como contrato interno.
"""

from typing import Any, Dict


def emit_event(event_type: str, payload: Dict[str, Any]) -> None:
    try:
        print(f"[CRM_UPDATE_ENGINE][EVENT] {event_type} {payload}")
    except Exception:
        pass
