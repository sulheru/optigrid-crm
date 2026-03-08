from django.db import models


class AIRecommendation(models.Model):

    scope_type = models.CharField(max_length=50)

    scope_id = models.CharField(max_length=100)

    recommendation_type = models.CharField(max_length=100)

    recommendation_text = models.TextField()

    confidence = models.FloatField()

    status = models.CharField(max_length=50, default="active")

    created_at = models.DateTimeField(auto_now_add=True)

