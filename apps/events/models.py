# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/events/models.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
from django.db import models


class Event(models.Model):

    event_type = models.CharField(max_length=100)

    aggregate_type = models.CharField(max_length=100)

    aggregate_id = models.CharField(max_length=100)

    payload = models.JSONField()

    triggered_by_type = models.CharField(max_length=50)

    triggered_by_id = models.CharField(max_length=100, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

