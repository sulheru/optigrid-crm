import hashlib
from collections import defaultdict
from statistics import mean

from apps.knowledge.models import KnowledgeCandidate
from apps.knowledge.services.embeddings import cosine_similarity, embed_text
from apps.knowledge.services.extraction import ExtractedSignal, collect_recent_email_signals


def _signature_for_cluster(candidate_type: str, examples: list[dict], canonical_text: str) -> str:
    source_keys = sorted(
        f"{example.get('source_model')}:{example.get('source_pk')}:{example.get('kind')}"
        for example in examples
    )
    raw = f"{candidate_type}|{canonical_text}|{'|'.join(source_keys)}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _cluster_signals(
    signals: list[ExtractedSignal],
    similarity_threshold: float = 0.78,
) -> list[list[ExtractedSignal]]:
    clusters: list[list[ExtractedSignal]] = []
    cluster_centroids: list[list[float]] = []

    for signal in signals:
        vector = embed_text(signal.text)
        best_idx = None
        best_score = 0.0

        for idx, centroid in enumerate(cluster_centroids):
            score = cosine_similarity(vector, centroid)
            if score > best_score:
                best_idx = idx
                best_score = score

        if best_idx is not None and best_score >= similarity_threshold:
            clusters[best_idx].append(signal)

            member_vectors = [embed_text(item.text) for item in clusters[best_idx]]
            dims = len(member_vectors[0]) if member_vectors else 0
            centroid = []
            for i in range(dims):
                centroid.append(sum(v[i] for v in member_vectors) / len(member_vectors))
            cluster_centroids[best_idx] = centroid
        else:
            clusters.append([signal])
            cluster_centroids.append(vector)

    return clusters


def _faq_payload(cluster: list[ExtractedSignal]) -> tuple[str, dict]:
    canonical_question = max(cluster, key=lambda item: len(item.text)).text.strip()
    content = (
        f"Question:\n{canonical_question}\n\n"
        "Answer guidance:\n"
        "Recurring inbound question detected. Review the source examples and define a canonical answer.\n"
    )
    metadata = {
        "canonical_question": canonical_question,
        "source_kind": "email_harvest",
        "cluster_size": len(cluster),
    }
    return content, metadata


def _behavior_payload(cluster: list[ExtractedSignal]) -> tuple[str, dict]:
    canonical_line = max(cluster, key=lambda item: len(item.text)).text.strip()
    name = canonical_line[:80]
    content = (
        f"Behavior name:\n{name}\n\n"
        "Operational instruction:\n"
        f"{canonical_line}\n"
    )
    metadata = {
        "behavior_name": name,
        "instruction": canonical_line,
        "source_kind": "email_harvest",
        "cluster_size": len(cluster),
    }
    return content, metadata


def generate_knowledge_candidates(
    *,
    limit: int = 200,
    similarity_threshold: float = 0.78,
    min_cluster_size: int = 2,
) -> dict:
    signals = collect_recent_email_signals(limit=limit)
    by_type: dict[str, list[ExtractedSignal]] = defaultdict(list)
    for signal in signals:
        by_type[signal.signal_type].append(signal)

    created = 0
    reused = 0

    for candidate_type, type_signals in by_type.items():
        clusters = _cluster_signals(type_signals, similarity_threshold=similarity_threshold)
        for cluster in clusters:
            if len(cluster) < min_cluster_size:
                continue

            if candidate_type == KnowledgeCandidate.CandidateType.FAQ:
                content, base_metadata = _faq_payload(cluster)
            elif candidate_type == KnowledgeCandidate.CandidateType.BEHAVIOR:
                content, base_metadata = _behavior_payload(cluster)
            else:
                continue

            source_examples = [item.metadata for item in cluster[:10]]
            signature = _signature_for_cluster(
                candidate_type=candidate_type,
                examples=source_examples,
                canonical_text=content,
            )

            pairwise = []
            for idx, left in enumerate(cluster):
                for right in cluster[idx + 1 :]:
                    pairwise.append(cosine_similarity(embed_text(left.text), embed_text(right.text)))

            confidence_score = min(
                0.99,
                0.45
                + min(len(cluster), 6) * 0.07
                + (mean(pairwise) if pairwise else 0.0) * 0.15,
            )

            obj, was_created = KnowledgeCandidate.objects.get_or_create(
                source_signature=signature,
                defaults={
                    "candidate_type": candidate_type,
                    "content": content,
                    "confidence_score": round(confidence_score, 4),
                    "source_examples": source_examples,
                    "metadata": base_metadata | {
                        "avg_similarity": round(mean(pairwise), 4) if pairwise else 1.0,
                    },
                },
            )
            if was_created:
                created += 1
            else:
                reused += 1
                if obj.status == KnowledgeCandidate.Status.PROPOSED:
                    obj.confidence_score = max(obj.confidence_score, round(confidence_score, 4))
                    obj.source_examples = source_examples
                    obj.metadata = base_metadata | {
                        "avg_similarity": round(mean(pairwise), 4) if pairwise else 1.0,
                    }
                    obj.content = content
                    obj.save(update_fields=["confidence_score", "source_examples", "metadata", "content"])

    return {
        "signals": len(signals),
        "created": created,
        "reused": reused,
    }
