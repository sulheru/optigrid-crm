from django.db import models


class InferenceRecord(models.Model):
    """
    V0 mínimo:
    - separado de facts
    - ligado a fuente
    - sin IA todavía (rule-based)
    """

    source_type = models.CharField(max_length=50)
    source_id = models.IntegerField()

    inference_type = models.CharField(max_length=100)
    payload = models.JSONField(default=dict, blank=True)

    confidence = models.FloatField(default=0.5)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.inference_type} ({self.source_type}:{self.source_id})"
