from django.test import TestCase
from django.utils import timezone

from apps.crm_update_engine.entrypoints import process_email
from apps.emailing.models import InboundEmail
from apps.opportunities.models import Opportunity
from apps.facts.models import FactRecord
from apps.inferences.models import InferenceRecord
from apps.updates.models import CRMUpdateProposal
from apps.recommendations.models import AIRecommendation


class CRMUpdateEngineIntegrationTests(TestCase):
    def _create_email(self, subject, body):
        # Crear Opportunity con lo mínimo posible (sin asumir campos)
        opportunity = Opportunity.objects.create()

        return InboundEmail.objects.create(
            from_email="sender@example.com",
            subject=subject,
            body=body,
            received_at=timezone.now(),
            opportunity=opportunity,
        )

    def test_process_email_is_idempotent_for_same_email(self):
        email = self._create_email(
            subject="Test inbound",
            body="Hello, this email has content.",
        )

        process_email(email)
        process_email(email)

        self.assertEqual(
            FactRecord.objects.filter(
                source_type="inbound_email",
                source_id=email.id,
                fact_type="email_received",
            ).count(),
            1,
        )

        self.assertEqual(
            InferenceRecord.objects.filter(
                source_type="inbound_email",
                source_id=email.id,
                inference_type="email_has_content",
            ).count(),
            1,
        )

        self.assertEqual(
            CRMUpdateProposal.objects.filter(
                source_type="inbound_email",
                source_id=email.id,
            ).count(),
            1,
        )

        recommendation_qs = AIRecommendation.objects.filter(
            scope_type="inbound_email",
            scope_id=email.id,
        )

        if AIRecommendation.objects.filter(source="crm_update_engine").exists():
            recommendation_qs = recommendation_qs.filter(source="crm_update_engine")

        self.assertEqual(recommendation_qs.count(), 1)

    def test_process_email_detects_pricing_signal(self):
        email = self._create_email(
            subject="Pricing question",
            body="Can you share price and budget guidance?",
        )

        process_email(email)

        self.assertTrue(
            InferenceRecord.objects.filter(
                source_type="inbound_email",
                source_id=email.id,
                inference_type="pricing_interest_signal",
            ).exists()
        )

        self.assertTrue(
            CRMUpdateProposal.objects.filter(
                source_type="inbound_email",
                source_id=email.id,
                proposal_type="prepare_pricing_response",
            ).exists()
        )
