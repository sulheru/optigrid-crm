import re
from dataclasses import dataclass
from typing import Any, Iterable, List

from django.apps import apps

from apps.knowledge.services.embeddings import upsert_vector_memory


QUESTION_RE = re.compile(r"([^\n\r\?]{8,}\?)")
BEHAVIOR_HINTS = (
    "please",
    "por favor",
    "send",
    "envía",
    "enviad",
    "use teams",
    "usa teams",
    "call me",
    "llámame",
    "write me in",
    "escríbeme en",
    "next week",
    "la próxima semana",
    "next month",
    "el mes que viene",
    "budget",
    "presupuesto",
    "pricing",
    "precio",
    "quote",
    "cotización",
)


@dataclass
class ExtractedSignal:
    signal_type: str
    text: str
    metadata: dict


def _safe_model_candidates():
    candidates = [
        ("emailing", "InboundEmail"),
        ("emailing", "EmailMessage"),
    ]
    for app_label, model_name in candidates:
        try:
            yield apps.get_model(app_label, model_name)
        except LookupError:
            continue


def _pick_text(obj: Any, field_names: Iterable[str]) -> str:
    values: List[str] = []
    for field_name in field_names:
        if hasattr(obj, field_name):
            value = getattr(obj, field_name)
            if value:
                values.append(str(value))
    return "\n".join(v.strip() for v in values if str(v).strip())


def _extract_questions(text: str) -> list[str]:
    found = []
    for match in QUESTION_RE.finditer(text):
        question = re.sub(r"\s+", " ", match.group(1)).strip()
        if len(question) >= 8:
            found.append(question)
    return found[:5]


def _extract_behavior_lines(text: str) -> list[str]:
    lines = []
    for raw_line in text.splitlines():
        line = re.sub(r"\s+", " ", raw_line).strip()
        if len(line) < 12:
            continue
        line_lower = line.lower()
        if any(hint in line_lower for hint in BEHAVIOR_HINTS):
            lines.append(line)
    return lines[:5]


def _source_example(obj: Any, text: str) -> dict:
    model_label = obj.__class__._meta.label
    pk = getattr(obj, "pk", None)
    subject = getattr(obj, "subject", "") or getattr(obj, "title", "")
    return {
        "source_model": model_label,
        "source_pk": pk,
        "subject": str(subject)[:200],
        "snippet": text[:400],
    }


def extract_email_signals_from_instance(obj: Any) -> list[ExtractedSignal]:
    subject = _pick_text(obj, ["subject"])
    body = _pick_text(
        obj,
        [
            "body_text",
            "body",
            "text",
            "content",
            "snippet",
            "body_html",
            "raw_body",
        ],
    )
    full_text = "\n".join(part for part in [subject, body] if part).strip()
    if not full_text:
        return []

    example = _source_example(obj, full_text)
    signals: list[ExtractedSignal] = []

    upsert_vector_memory(
        namespace="email_knowledge_raw",
        source_model=obj.__class__._meta.label,
        source_pk=str(getattr(obj, "pk", "")),
        source_text=full_text,
        metadata=example,
    )

    for question in _extract_questions(full_text):
        signals.append(
            ExtractedSignal(
                signal_type="FAQ",
                text=question,
                metadata=example | {"kind": "question"},
            )
        )

    for line in _extract_behavior_lines(full_text):
        signals.append(
            ExtractedSignal(
                signal_type="BEHAVIOR",
                text=line,
                metadata=example | {"kind": "behavior_hint"},
            )
        )

    return signals


def collect_recent_email_signals(limit: int = 200) -> list[ExtractedSignal]:
    results: list[ExtractedSignal] = []
    for model in _safe_model_candidates():
        queryset = model.objects.all().order_by("-pk")[:limit]
        for obj in queryset:
            results.extend(extract_email_signals_from_instance(obj))
        if results:
            break
    return results
