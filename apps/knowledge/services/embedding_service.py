from apps.knowledge.models import KnowledgeEmbedding
from .vector_memory import simple_embedding


def create_embedding_for_candidate(candidate):
    vec = simple_embedding(candidate.content)

    KnowledgeEmbedding.objects.create(
        candidate=candidate,
        vector=vec,
    )

    return vec
