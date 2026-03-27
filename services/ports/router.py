from __future__ import annotations

from services.ports.registry import get_registered_ports, register_default_ports


class PortRouter:
    def __init__(self) -> None:
        register_default_ports()

    def resolve(self, intent):
        registered = get_registered_ports()

        if getattr(intent, "adapter_key", ""):
            adapter_key = intent.adapter_key
            if adapter_key not in registered:
                raise LookupError(f"Adapter not registered: {adapter_key}")
            return registered[adapter_key]

        provider = getattr(intent, "provider", "") or "m365"
        port_name = getattr(intent, "port_name", "")

        candidate_key = f"{provider}.{port_name}"
        if candidate_key in registered:
            return registered[candidate_key]

        raise LookupError(f"No adapter registered for provider={provider} port={port_name}")


_router = PortRouter()


def get_port_router() -> PortRouter:
    return _router
