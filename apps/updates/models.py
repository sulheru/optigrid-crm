from django.db import models


class CRMUpdateProposal(models.Model):
    source_type = models.CharField(max_length=50)
    source_id = models.CharField(max_length=50)
    proposal_type = models.CharField(max_length=100)
    payload = models.JSONField(default=dict)
    status = models.CharField(max_length=50, default="proposed")


class RuleEvaluationLog(models.Model):
    source_type = models.CharField(max_length=50)
    source_id = models.CharField(max_length=50)

    trace = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.source_type}:{self.source_id} @ {self.created_at}"
