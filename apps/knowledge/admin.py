from django.contrib import admin

from .models import (
    Behavior,
    FAQ,
    KnowledgeCandidate,
    KnowledgeEmbedding,
)


@admin.register(Behavior)
class BehaviorAdmin(admin.ModelAdmin):
    list_display = ("id", "key", "value")


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "answer")


@admin.register(KnowledgeCandidate)
class KnowledgeCandidateAdmin(admin.ModelAdmin):
    list_display = ("id", "type", "status", "confidence_score")
    list_filter = ("type", "status")
    search_fields = ("content", "source_signature")


@admin.register(KnowledgeEmbedding)
class KnowledgeEmbeddingAdmin(admin.ModelAdmin):
    list_display = ("id", "content", "created_at")
