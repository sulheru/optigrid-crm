from django.db import models


class FactRecord(models.Model):
    """
    V0 mínimo:
    - ligado a email
    - payload libre
    - separación clara (no inferencias)
    """

    source_type = models.CharField(max_length=50)
    source_id = models.IntegerField()

    fact_type = models.CharField(max_length=100)
    payload = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.fact_type} ({self.source_type}:{self.source_id})"
