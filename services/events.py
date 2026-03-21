# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/services/events.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
from __future__ import annotations

from typing import Any

from apps.events.models import Event


def record_event(
    *,
    event_type: str,
    aggregate_type: str,
    aggregate_id: int,
    payload: dict[str, Any] | None = None,
    triggered_by_type: str = "system",
    triggered_by_id: str = "",
) -> Event:
    """
    Registra un evento de dominio en la tabla Event.
    """
    return Event.objects.create(
        event_type=event_type,
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        payload=payload or {},
        triggered_by_type=triggered_by_type,
        triggered_by_id=triggered_by_id,
    )
