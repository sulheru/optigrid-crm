# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/events/models.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
from django.db import models


class ActivityEvent(models.Model):
    event_type = models.CharField(max_length=100)
    entity_type = models.CharField(max_length=100, null=True, blank=True)
    entity_id = models.IntegerField(null=True, blank=True)

    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event_type} ({self.entity_type}:{self.entity_id})"
