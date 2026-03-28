from apps.knowledge.models import KnowledgeCandidate, FAQ, Behavior


def accept_candidate(candidate: KnowledgeCandidate):

    if candidate.type == KnowledgeCandidate.Type.FAQ:
        FAQ.objects.create(
            question=candidate.content,
            answer="TO_BE_DEFINED",
        )

    elif candidate.type == KnowledgeCandidate.Type.BEHAVIOR:
        Behavior.objects.create(
            description=candidate.content,
        )

    candidate.status = KnowledgeCandidate.Status.ACCEPTED
    candidate.save()

    return candidate


def reject_candidate(candidate: KnowledgeCandidate):
    candidate.status = KnowledgeCandidate.Status.REJECTED
    candidate.save()
    return candidate
