from django.contrib import admin

from .models import (
    KnowledgeCandidate,
    KnowledgeEmbedding,
    FAQ,
    Behavior,
)


@admin.register(KnowledgeCandidate)
class KnowledgeCandidateAdmin(admin.ModelAdmin):
    list_display = ("id", "type", "status", "confidence_score", "created_at")
    list_filter = ("type", "status")
    search_fields = ("content",)


@admin.register(KnowledgeEmbedding)
class KnowledgeEmbeddingAdmin(admin.ModelAdmin):
    list_display = ("id", "candidate", "created_at")


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("id", "is_active", "version", "created_at")
    search_fields = ("question", "answer")


@admin.register(Behavior)
class BehaviorAdmin(admin.ModelAdmin):
    list_display = ("id", "is_active", "version", "created_at")
    search_fields = ("description",)
