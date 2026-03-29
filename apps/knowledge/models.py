from django.db import models


class KnowledgeCandidate(models.Model):
    class CandidateType(models.TextChoices):
        FAQ = "faq", "FAQ"
        BEHAVIOR = "behavior", "Behavior"

    class Status(models.TextChoices):
        NEW = "new", "New"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"

    type = models.CharField(max_length=50, choices=CandidateType.choices)
    candidate_type = models.CharField(max_length=50, choices=CandidateType.choices)
    content = models.TextField()

    source = models.CharField(max_length=255, default="system")

    confidence_score = models.FloatField(default=0.0)
    metadata = models.JSONField(default=dict, blank=True)
    source_signature = models.CharField(max_length=255, blank=True, default="")

    status = models.CharField(max_length=50, choices=Status.choices, default=Status.NEW)


class BehaviorEntry(models.Model):
    key = models.CharField(max_length=255)
    value = models.TextField()


class FAQEntry(models.Model):
    question = models.TextField()
    answer = models.TextField()


class VectorMemoryItem(models.Model):
    namespace = models.CharField(max_length=100)
    key = models.CharField(max_length=255)
    content = models.TextField()
    embedding = models.JSONField()

    # 🔴 NUEVO CAMPO
    metadata = models.JSONField(default=dict, blank=True)

    source_model = models.CharField(max_length=100, blank=True, default="")
    source_pk = models.CharField(max_length=100, blank=True, default="")


class KnowledgeEmbedding(models.Model):
    content = models.TextField(blank=True, default="")
    vector = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)


class Behavior(BehaviorEntry):
    class Meta:
        proxy = True


class FAQ(FAQEntry):
    class Meta:
        proxy = True
