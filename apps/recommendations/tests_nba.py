from django.test import TestCase

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
