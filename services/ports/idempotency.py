from __future__ import annotations

import hashlib
import json


def _stable_json(data) -> str:
    return json.dumps(data or {}, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def build_intent_idempotency_key(intent) -> str:
    semantic_fingerprint = hashlib.sha256(
        _stable_json(
            {
                "provider": getattr(intent, "provider", ""),
                "payload": getattr(intent, "payload", {}),
                "target_ref_type": getattr(intent, "target_ref_type", ""),
                "target_ref_id": getattr(intent, "target_ref_id", ""),
            }
        ).encode("utf-8")
    ).hexdigest()[:24]

    return "|".join(
        [
            getattr(intent, "intent_type", ""),
            f"{getattr(intent, 'target_ref_type', '')}:{getattr(intent, 'target_ref_id', '')}",
            semantic_fingerprint,
            "v1",
        ]
    )
