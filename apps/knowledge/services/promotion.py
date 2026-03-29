from apps.knowledge.models import (
    KnowledgeCandidate,
    BehaviorEntry,
    FAQEntry,
)


def accept_candidate(candidate: KnowledgeCandidate):
    if candidate.candidate_type == KnowledgeCandidate.CandidateType.FAQ:
        obj = FAQEntry.objects.create(
            question=candidate.content,
            answer="",
        )
    elif candidate.candidate_type == KnowledgeCandidate.CandidateType.BEHAVIOR:
        obj = BehaviorEntry.objects.create(
            key=candidate.content,
            value="",
        )
    else:
        return None

    candidate.status = KnowledgeCandidate.Status.ACCEPTED
    candidate.save(update_fields=["status"])
    return obj


def reject_candidate(candidate: KnowledgeCandidate):
    candidate.status = KnowledgeCandidate.Status.REJECTED
    candidate.save(update_fields=["status"])
    return candidate
