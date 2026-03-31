from django.db import models


class CRMUpdateProposal(models.Model):
    """
    V0 mínimo:
    - propuesta generada por el engine
    - no ejecuta nada todavía
    """

    source_type = models.CharField(max_length=50)
    source_id = models.IntegerField()

    proposal_type = models.CharField(max_length=100)
    payload = models.JSONField(default=dict, blank=True)

    status = models.CharField(
        max_length=50,
        default="proposed",  # proposed | approved | rejected | applied
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.proposal_type} ({self.source_type}:{self.source_id})"
