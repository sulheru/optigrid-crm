from django.db import models


class CRMUpdateProposal(models.Model):

    target_entity_type = models.CharField(max_length=50)

    target_entity_id = models.CharField(max_length=100)

    proposed_change_type = models.CharField(max_length=100)

    proposed_payload = models.JSONField()

    confidence = models.FloatField()

    approval_required = models.BooleanField(default=True)

    proposal_status = models.CharField(max_length=50, default="proposed")

    created_at = models.DateTimeField(auto_now_add=True)

