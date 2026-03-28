from apps.knowledge.models import KnowledgeCandidate


def extract_from_email(email):

    text = (email.subject or "") + "\n" + (email.body or "")

    candidates = []

    # Heurística básica
    if "?" in text:
        candidates.append(
            KnowledgeCandidate(
                type=KnowledgeCandidate.Type.FAQ,
                content=text[:500],
                confidence_score=0.6,
                source_examples=text[:500],
            )
        )

    if any(x in text.lower() for x in ["please", "could you", "next step"]):
        candidates.append(
            KnowledgeCandidate(
                type=KnowledgeCandidate.Type.BEHAVIOR,
                content=text[:500],
                confidence_score=0.5,
                source_examples=text[:500],
            )
        )

    return candidates
