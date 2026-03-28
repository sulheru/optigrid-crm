from apps.knowledge.models import KnowledgeCandidate
from apps.knowledge.services.vector_memory import cosine_similarity
from apps.knowledge.services.embedding_service import create_embedding_for_candidate


SIMILARITY_THRESHOLD = 0.85


def generate_candidates(new_candidates):

    created = []

    existing = list(KnowledgeCandidate.objects.all())

    for candidate in new_candidates:

        vec_new = create_embedding_for_candidate(candidate)

        is_duplicate = False

        for ex in existing:
            if not ex.embeddings.exists():
                continue

            vec_old = ex.embeddings.first().vector

            sim = cosine_similarity(vec_new, vec_old)

            if sim > SIMILARITY_THRESHOLD:
                is_duplicate = True
                break

        if not is_duplicate:
            candidate.save()
            created.append(candidate)

    return created
