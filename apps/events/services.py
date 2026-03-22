# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/events/services.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
from apps.events.models import ActivityEvent


def log_event(event_type, entity_type=None, entity_id=None, metadata=None):
    ActivityEvent.objects.create(
        event_type=event_type,
        entity_type=entity_type,
        entity_id=entity_id,
        metadata=metadata or {},
    )
