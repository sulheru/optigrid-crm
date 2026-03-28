import math
import hashlib


def simple_embedding(text: str):
    """
    Embedding determinista simple (NO LLM).
    """
    text = text.lower().strip()

    tokens = text.split()

    vec = {}

    for t in tokens:
        h = int(hashlib.md5(t.encode()).hexdigest(), 16)
        bucket = h % 128
        vec[bucket] = vec.get(bucket, 0) + 1

    return vec


def cosine_similarity(a: dict, b: dict) -> float:
    keys = set(a.keys()) | set(b.keys())

    dot = sum(a.get(k, 0) * b.get(k, 0) for k in keys)

    norm_a = math.sqrt(sum(v * v for v in a.values()))
    norm_b = math.sqrt(sum(v * v for v in b.values()))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)
