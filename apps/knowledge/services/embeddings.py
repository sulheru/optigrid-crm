import math
import hashlib

from apps.knowledge.models import VectorMemoryItem


def embed_text(text: str):
    return [float(ord(c)) for c in text[:50]]


def cosine_similarity(a, b):
    if not a or not b:
        return 0.0

    min_len = min(len(a), len(b))
    a = a[:min_len]
    b = b[:min_len]

    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


def _generate_key(namespace, content):
    base = f"{namespace}:{content or ''}"
    return hashlib.sha256(base.encode()).hexdigest()


def upsert_vector_memory(*args, **kwargs):
    namespace = kwargs.get("namespace") or (args[0] if len(args) > 0 else "default")

    content = kwargs.get("content") or (args[1] if len(args) > 1 else "")
    embedding = kwargs.get("embedding") or embed_text(content)

    metadata = kwargs.get("metadata", {})

    key = kwargs.get("key") or _generate_key(namespace, content)

    obj, _ = VectorMemoryItem.objects.update_or_create(
        namespace=namespace,
        key=key,
        defaults={
            "content": content,
            "embedding": embedding,
            "metadata": metadata,  # 🔴 FIX CLAVE
            "source_model": kwargs.get("source_model", ""),
            "source_pk": str(kwargs.get("source_pk", "")),
        },
    )
    return obj
