from django.db import models
from django.utils import timezone


class KnowledgeCandidate(models.Model):

    class Type(models.TextChoices):
        FAQ = "faq", "FAQ"
        BEHAVIOR = "behavior", "Behavior"
        CAPABILITY = "capability", "Capability Proposal"

    class Status(models.TextChoices):
        PROPOSED = "proposed", "Proposed"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"

    type = models.CharField(max_length=32, choices=Type.choices)

    content = models.TextField()

    confidence_score = models.FloatField(default=0.0)

    source_examples = models.TextField(blank=True, default="")

    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.PROPOSED,
    )

    metadata = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.type} | {self.status} | {self.content[:60]}"


class KnowledgeEmbedding(models.Model):

    candidate = models.ForeignKey(
        KnowledgeCandidate,
        on_delete=models.CASCADE,
        related_name="embeddings",
    )

    vector = models.JSONField()

    created_at = models.DateTimeField(default=timezone.now)


class FAQ(models.Model):
    question = models.TextField()
    answer = models.TextField()

    is_active = models.BooleanField(default=True)

    version = models.IntegerField(default=1)

    created_at = models.DateTimeField(default=timezone.now)


class Behavior(models.Model):
    description = models.TextField()

    is_active = models.BooleanField(default=True)

    version = models.IntegerField(default=1)

    created_at = models.DateTimeField(default=timezone.now)
