import math
import re
from typing import Iterable, List

from apps.knowledge.models import VectorMemoryItem


TOKEN_RE = re.compile(r"[a-z0-9áéíóúüñ]{2,}", re.IGNORECASE)
DEFAULT_DIMENSIONS = 128


def tokenize(text: str) -> List[str]:
    if not text:
        return []
    return [m.group(0).lower() for m in TOKEN_RE.finditer(text)]


def embed_text(text: str, dimensions: int = DEFAULT_DIMENSIONS) -> List[float]:
    tokens = tokenize(text)
    if not tokens:
        return [0.0] * dimensions

    vector = [0.0] * dimensions
    for token in tokens:
        idx = hash(token) % dimensions
        vector[idx] += 1.0

    norm = math.sqrt(sum(v * v for v in vector))
    if norm == 0:
        return vector

    return [v / norm for v in vector]


def cosine_similarity(left: Iterable[float], right: Iterable[float]) -> float:
    left = list(left)
    right = list(right)
    if not left or not right or len(left) != len(right):
        return 0.0

    num = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))

    if left_norm == 0 or right_norm == 0:
        return 0.0

    return num / (left_norm * right_norm)


def upsert_vector_memory(
    *,
    namespace: str,
    source_model: str,
    source_pk: str,
    source_text: str,
    metadata: dict | None = None,
) -> VectorMemoryItem:
    embedding = embed_text(source_text)
    obj, _ = VectorMemoryItem.objects.update_or_create(
        namespace=namespace,
        source_model=source_model,
        source_pk=str(source_pk),
        defaults={
            "source_text": source_text,
            "embedding": embedding,
            "metadata": metadata or {},
        },
    )
    return obj
