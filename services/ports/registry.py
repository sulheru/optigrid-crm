from __future__ import annotations

from typing import Dict

from services.adapters.m365.calendar import M365CalendarPort
from services.adapters.m365.mail import M365MailPort

_PORTS: Dict[str, object] = {}


def register_port(port) -> None:
    _PORTS[port.adapter_key] = port


def get_registered_ports() -> dict[str, object]:
    return dict(_PORTS)


def register_default_ports() -> None:
    if _PORTS:
        return
    register_port(M365MailPort())
    register_port(M365CalendarPort())
