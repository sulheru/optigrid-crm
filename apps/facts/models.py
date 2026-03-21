# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/facts/models.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
from django.db import models


class FactRecord(models.Model):

    source_type = models.CharField(max_length=50)

    source_id = models.CharField(max_length=100)

    fact_type = models.CharField(max_length=100)

    fact_value = models.TextField()

    confidence = models.FloatField(default=0.0)

    observed_at = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)

