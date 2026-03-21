# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/inferences/models.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
from django.db import models


class InferenceRecord(models.Model):

    source_type = models.CharField(max_length=50)

    source_id = models.CharField(max_length=100)

    inference_type = models.CharField(max_length=100)

    inference_value = models.TextField()

    confidence = models.FloatField()

    rationale = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

