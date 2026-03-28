from django.test import TestCase

from apps.knowledge.models import BehaviorEntry, FAQEntry, KnowledgeCandidate, VectorMemoryItem
from apps.knowledge.services.embeddings import cosine_similarity, embed_text, upsert_vector_memory
from apps.knowledge.services.promotion import accept_candidate, reject_candidate


class EmbeddingTests(TestCase):
    def test_similarity_is_higher_for_related_text(self):
        a = embed_text("How much does it cost for an infrastructure assessment?")
        b = embed_text("What is the price of the infrastructure assessment?")
        c = embed_text("The cat is sleeping on the sofa.")

        self.assertGreater(cosine_similarity(a, b), cosine_similarity(a, c))

    def test_upsert_vector_memory_is_idempotent(self):
        first = upsert_vector_memory(
            namespace="test",
            source_model="emailing.InboundEmail",
            source_pk="1",
            source_text="hello world",
            metadata={"a": 1},
        )
        second = upsert_vector_memory(
            namespace="test",
            source_model="emailing.InboundEmail",
            source_pk="1",
            source_text="hello world updated",
            metadata={"a": 2},
        )

        self.assertEqual(first.pk, second.pk)
        self.assertEqual(VectorMemoryItem.objects.count(), 1)
        self.assertEqual(VectorMemoryItem.objects.first().metadata["a"], 2)


class PromotionTests(TestCase):
    def test_accept_faq_candidate_promotes_to_faq_entry(self):
        candidate = KnowledgeCandidate.objects.create(
            candidate_type=KnowledgeCandidate.CandidateType.FAQ,
            content="Question:\nWhat is the price?\n\nAnswer guidance:\nExplain scope first.\n",
            confidence_score=0.8,
            metadata={"canonical_question": "What is the price?"},
            source_signature="faq-test-signature",
        )

        promoted = accept_candidate(candidate)
        candidate.refresh_from_db()

        self.assertEqual(candidate.status, KnowledgeCandidate.Status.ACCEPTED)
        self.assertIsInstance(promoted, FAQEntry)
        self.assertEqual(FAQEntry.objects.count(), 1)

    def test_accept_behavior_candidate_promotes_to_behavior_entry(self):
        candidate = KnowledgeCandidate.objects.create(
            candidate_type=KnowledgeCandidate.CandidateType.BEHAVIOR,
            content="Behavior name:\nPricing framing\n\nOperational instruction:\nAlways clarify scope before quoting price.\n",
            confidence_score=0.75,
            metadata={
                "behavior_name": "Pricing framing",
                "instruction": "Always clarify scope before quoting price.",
            },
            source_signature="behavior-test-signature",
        )

        promoted = accept_candidate(candidate)
        candidate.refresh_from_db()

        self.assertEqual(candidate.status, KnowledgeCandidate.Status.ACCEPTED)
        self.assertIsInstance(promoted, BehaviorEntry)
        self.assertEqual(BehaviorEntry.objects.count(), 1)

    def test_reject_candidate_marks_rejected(self):
        candidate = KnowledgeCandidate.objects.create(
            candidate_type=KnowledgeCandidate.CandidateType.FAQ,
            content="Question:\nDummy?\n",
            confidence_score=0.2,
            source_signature="reject-test-signature",
        )

        reject_candidate(candidate)
        candidate.refresh_from_db()

        self.assertEqual(candidate.status, KnowledgeCandidate.Status.REJECTED)
