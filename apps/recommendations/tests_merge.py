from django.test import SimpleTestCase

from apps.recommendations.merge import merge_recommendation_candidates
from apps.recommendations.models import AIRecommendation


class RecommendationMergeTests(SimpleTestCase):
    def build_rec(self, source, rec_type="followup", text="x", confidence=0.5):
        return AIRecommendation(
            scope_type="email_thread",
            scope_id="thread-1",
            recommendation_type=rec_type,
            recommendation_text=text,
            confidence=confidence,
            status=AIRecommendation.STATUS_NEW,
            source=source,
        )

    def test_rules_priority_over_llm(self):
        rules = self.build_rec("rules", text="Follow up in 5 days", confidence=0.7)
        llm = self.build_rec("llm", text="Mention budget angle", confidence=0.9)

        result = merge_recommendation_candidates([rules, llm])

        self.assertEqual(len(result.kept), 1)
        self.assertEqual(result.kept[0].source, "merged")
        self.assertIn("Follow up in 5 days", result.kept[0].recommendation_text)
        self.assertIn("Mention budget angle", result.kept[0].recommendation_text)

    def test_llm_only_keeps_best(self):
        a = self.build_rec("llm", text="A", confidence=0.4)
        b = self.build_rec("llm", text="B", confidence=0.9)

        result = merge_recommendation_candidates([a, b])

        self.assertEqual(len(result.kept), 1)
        self.assertEqual(result.kept[0].source, "llm")
        self.assertEqual(result.kept[0].recommendation_text, "B")

    def test_rules_only_deduplicates(self):
        a = self.build_rec("rules", text="A", confidence=0.4)
        b = self.build_rec("rules", text="B", confidence=0.8)

        result = merge_recommendation_candidates([a, b])

        self.assertEqual(len(result.kept), 1)
        self.assertEqual(result.kept[0].source, "rules")
        self.assertEqual(result.kept[0].recommendation_text, "B")
