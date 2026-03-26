from django.test import TestCase

from apps.recommendations.models import AIRecommendation
from apps.recommendations.nba import (
    compute_score,
    get_next_best_action,
    get_next_best_action_explained,
    get_score_breakdown,
)


class NBATests(TestCase):
    def _make_rec(
        self,
        *,
        recommendation_type,
        priority=0,
        confidence=0.5,
        urgency=0,
        status="new",
    ):
        rec = AIRecommendation.objects.create(
            recommendation_type=recommendation_type,
            recommendation_text=f"{recommendation_type} recommendation",
            status=status,
            confidence=confidence,  # ✅ REQUIRED FIELD
        )

        # Runtime attributes
        rec.priority_score = priority
        rec.urgency_score = urgency

        return rec

    def test_compute_score_returns_weighted_total(self):
        rec = self._make_rec(
            recommendation_type="followup",
            priority=10,
            confidence=0.8,
            urgency=5,
        )

        score = compute_score(rec)

        expected = (10 * 0.4) + (0.8 * 0.2) + (5 * 0.3) + (1.2 * 0.1)
        self.assertAlmostEqual(score, expected)

    def test_get_score_breakdown_exposes_all_components(self):
        rec = self._make_rec(
            recommendation_type="opportunity_review",
            priority=7,
            confidence=0.6,
            urgency=4,
        )

        breakdown = get_score_breakdown(rec)

        self.assertEqual(breakdown.priority_raw, 7.0)
        self.assertAlmostEqual(breakdown.priority_component, 2.8)
        self.assertEqual(breakdown.confidence_raw, 0.6)
        self.assertAlmostEqual(breakdown.confidence_component, 0.12)
        self.assertEqual(breakdown.urgency_raw, 4.0)
        self.assertAlmostEqual(breakdown.urgency_component, 1.2)
        self.assertEqual(breakdown.type_weight_raw, 1.3)

    def test_get_next_best_action_returns_highest_scored_recommendation(self):
        weaker = self._make_rec(
            recommendation_type="contact_strategy",
            priority=5,
            confidence=0.6,
            urgency=2,
        )
        stronger = self._make_rec(
            recommendation_type="followup",
            priority=9,
            confidence=0.9,
            urgency=6,
        )

        best = get_next_best_action(
            AIRecommendation.objects.filter(status="new")
        )

        self.assertEqual(best.id, stronger.id)
        self.assertNotEqual(best.id, weaker.id)

    def test_get_next_best_action_explained_returns_breakdown_and_alternatives(self):
        winner = self._make_rec(
            recommendation_type="opportunity_review",
            priority=10,
            confidence=0.9,
            urgency=7,
        )
        self._make_rec(
            recommendation_type="followup",
            priority=7,
            confidence=0.7,
            urgency=5,
        )
        self._make_rec(
            recommendation_type="reply_strategy",
            priority=6,
            confidence=0.8,
            urgency=4,
        )

        result = get_next_best_action_explained(
            AIRecommendation.objects.filter(status="new")
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.recommendation.id, winner.id)
        self.assertIn("highest total score", result.why_selected)
        self.assertGreaterEqual(len(result.alternatives), 2)

    def test_get_next_best_action_explained_returns_none_for_empty_queryset(self):
        result = get_next_best_action_explained(
            AIRecommendation.objects.filter(status="new")
        )
        self.assertIsNone(result)
