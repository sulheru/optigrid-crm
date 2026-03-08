from django.db import models


class InferenceRecord(models.Model):

    source_type = models.CharField(max_length=50)

    source_id = models.CharField(max_length=100)

    inference_type = models.CharField(max_length=100)

    inference_value = models.TextField()

    confidence = models.FloatField()

    rationale = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

