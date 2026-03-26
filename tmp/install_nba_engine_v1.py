from pathlib import Path
import re

ROOT = Path(".").resolve()

NBA_FILE = ROOT / "apps/recommendations/nba.py"
DASHBOARD_VIEWS = ROOT / "apps/dashboard_views.py"
NBA_TEMPLATE = ROOT / "templates/dashboard/partials/next_best_action.html"
TESTS_FILE = ROOT / "apps/recommendations/tests_nba.py"

NBA_CODE = """from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Optional

from django.db.models import QuerySet
from django.utils import timezone

from apps.recommendations.models import AIRecommendation


TYPE_WEIGHTS = {
    "followup": 1.0,
    "contact_strategy": 0.6,
    "opportunity_review": 0.5,
    "review": 0.3,
}


@dataclass(frozen=True)
class NBAResult:
    recommendation: AIRecommendation
    confidence_score: float
    urgency_score: float
    type_weight: float
    final_score: float


def get_type_weight(recommendation_type: str | None) -> float:
    if not recommendation_type:
        return 0.3
    return TYPE_WEIGHTS.get(recommendation_type, 0.3)


def get_urgency_score(recommendation: AIRecommendation) -> float:
    # V1 determinista, sin LLM.
    # Señales usadas:
    # - recencia
    # - hints textuales en rationale / text
    # - tipo followup como proxy de “sin respuesta / espera de acción”
    now = timezone.now()

    timestamps = [
        getattr(recommendation, "created_at", None),
        getattr(recommendation, "updated_at", None),
    ]
    timestamps = [ts for ts in timestamps if ts is not None]
    reference_ts = max(timestamps) if timestamps else None

    text_parts = [
        getattr(recommendation, "recommendation_text", "") or "",
        getattr(recommendation, "rationale", "") or "",
    ]
    text_blob = " ".join(text_parts).lower()

    recency_score = 0.2
    if reference_ts is not None:
        age = now - reference_ts
        if age <= timedelta(days=2):
            recency_score = 1.0
        elif age <= timedelta(days=7):
            recency_score = 0.7
        elif age <= timedelta(days=21):
            recency_score = 0.4
        else:
            recency_score = 0.2

    waiting_markers = [
        "no reply",
        "sin respuesta",
        "awaiting reply",
        "follow-up",
        "follow up",
        "seguimiento",
        "remind",
        "retomar",
    ]
    cold_markers = [
        "cold",
        "frío",
        "paused",
        "deferred",
        "later",
        "más adelante",
    ]

    if any(marker in text_blob for marker in waiting_markers):
        return max(recency_score, 0.6)

    if any(marker in text_blob for marker in cold_markers):
        return min(recency_score, 0.3)

    if getattr(recommendation, "recommendation_type", None) == "followup":
        return max(recency_score, 0.7)

    return recency_score


def get_recommendation_confidence(recommendation: AIRecommendation) -> float:
    raw = getattr(recommendation, "confidence", 0.0) or 0.0
    try:
        return float(raw)
    except (TypeError, ValueError):
        return 0.0


def score_recommendation(recommendation: AIRecommendation) -> NBAResult:
    confidence_score = get_recommendation_confidence(recommendation)
    urgency_score = get_urgency_score(recommendation)
    type_weight = get_type_weight(getattr(recommendation, "recommendation_type", None))
    final_score = confidence_score + urgency_score + type_weight

    return NBAResult(
        recommendation=recommendation,
        confidence_score=confidence_score,
        urgency_score=urgency_score,
        type_weight=type_weight,
        final_score=final_score,
    )


def _base_queryset() -> QuerySet[AIRecommendation]:
    qs = AIRecommendation.objects.all()

    status_field = getattr(AIRecommendation, "status", None)
    source_field = getattr(AIRecommendation, "source", None)

    if status_field is not None:
        try:
            qs = qs.filter(status="new")
        except Exception:
            # compatibilidad con estados legacy
            try:
                qs = qs.filter(status="active")
            except Exception:
                pass

    if source_field is not None:
        try:
            qs = qs.filter(source="merged")
        except Exception:
            pass

    return qs


def get_next_best_action() -> Optional[AIRecommendation]:
    scored = get_next_best_action_result()
    return scored.recommendation if scored else None


def get_next_best_action_result() -> Optional[NBAResult]:
    candidates = list(_base_queryset())
    if not candidates:
        return None

    scored = [score_recommendation(item) for item in candidates]
    scored.sort(
        key=lambda item: (
            item.final_score,
            item.urgency_score,
            item.confidence_score,
            item.recommendation.pk,
        ),
        reverse=True,
    )
    return scored[0]
"""

NBA_TEMPLATE_CODE = """{% if nba %}
<div class="card shadow-sm border-0 mb-4">
  <div class="card-body">
    <div class="d-flex justify-content-between align-items-start flex-wrap gap-3">
      <div>
        <div class="text-uppercase small text-muted mb-2">What should you do now</div>
        <h5 class="mb-2">
          {{ nba.recommendation_type|default:"Recommendation"|title }}
        </h5>
        <p class="mb-2">{{ nba.recommendation_text }}</p>
        {% if nba.rationale %}
          <p class="text-muted mb-0">{{ nba.rationale }}</p>
        {% endif %}
      </div>

      <div class="text-end">
        <div class="small text-muted">Score</div>
        <div class="h4 mb-2">{{ nba_score|floatformat:2 }}</div>
        <a href="/recommendations/{{ nba.id }}/execute/" class="btn btn-primary">
          Execute
        </a>
      </div>
    </div>
  </div>
</div>
{% endif %}
"""

TESTS_CODE = """from django.test import TestCase

from apps.recommendations.models import AIRecommendation
from apps.recommendations.nba import (
    get_next_best_action_result,
    get_type_weight,
    score_recommendation,
)


class NextBestActionEngineTests(TestCase):
    def test_type_weights_are_stable(self):
        self.assertEqual(get_type_weight("followup"), 1.0)
        self.assertEqual(get_type_weight("contact_strategy"), 0.6)
        self.assertEqual(get_type_weight("opportunity_review"), 0.5)
        self.assertEqual(get_type_weight("unknown_type"), 0.3)

    def test_returns_highest_scored_merged_new_recommendation(self):
        low = AIRecommendation.objects.create(
            recommendation_type="review",
            recommendation_text="Low priority review",
            confidence=0.2,
            status="new",
            source="merged",
        )
        high = AIRecommendation.objects.create(
            recommendation_type="followup",
            recommendation_text="Follow up with no reply",
            confidence=0.8,
            status="new",
            source="merged",
        )

        result = get_next_best_action_result()

        self.assertIsNotNone(result)
        self.assertEqual(result.recommendation.id, high.id)
        self.assertGreater(result.final_score, score_recommendation(low).final_score)
"""

def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"[ok] wrote {path}")


def patch_dashboard_views() -> None:
    text = DASHBOARD_VIEWS.read_text(encoding="utf-8")

    if "apps.recommendations.nba" not in text:
        text = re.sub(
            r"(^from .* import .*$)",
            r"\\1",
            text,
            count=1,
            flags=re.MULTILINE,
        )
        text = "from apps.recommendations.nba import get_next_best_action_result\\n" + text

    if "nba_result = get_next_best_action_result()" not in text:
        context_update = '''
    nba_result = get_next_best_action_result()
'''
        # intenta insertar dentro de la vista principal de dashboard
        text = re.sub(
            r"(def .*?(?:dashboard|home|index).*?:\\n(?:    .*\\n)+?)(\\s*context\\s*=\\s*\\{)",
            lambda m: m.group(1) + context_update + m.group(2),
            text,
            count=1,
            flags=re.MULTILINE,
        )

    if "'nba':" not in text and '"nba":' not in text:
        text = re.sub(
            r"(context\\s*=\\s*\\{)",
            r'''\\1
        "nba": nba_result.recommendation if nba_result else None,
        "nba_score": nba_result.final_score if nba_result else None,
        "nba_result": nba_result,
''',
            text,
            count=1,
        )

    DASHBOARD_VIEWS.write_text(text, encoding="utf-8")
    print(f"[ok] patched {DASHBOARD_VIEWS}")


def ensure_dashboard_partial_included() -> None:
    candidates = [
        ROOT / "templates/dashboard/home.html",
        ROOT / "templates/dashboard/index.html",
    ]

    include_line = '{% include "dashboard/partials/next_best_action.html" %}'

    for path in candidates:
        if not path.exists():
            continue

        text = path.read_text(encoding="utf-8")
        if include_line in text:
            print(f"[ok] include already present in {path}")
            continue

        if "{% block content %}" in text:
            text = text.replace("{% block content %}", "{% block content %}\\n" + include_line, 1)
        else:
            text = include_line + "\\n" + text

        path.write_text(text, encoding="utf-8")
        print(f"[ok] inserted partial include in {path}")


def main() -> None:
    write_file(NBA_FILE, NBA_CODE)
    write_file(NBA_TEMPLATE, NBA_TEMPLATE_CODE)
    write_file(TESTS_FILE, TESTS_CODE)
    patch_dashboard_views()
    ensure_dashboard_partial_included()
    print("\\nDone.")


if __name__ == "__main__":
    main()
