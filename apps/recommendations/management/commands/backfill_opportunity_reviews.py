# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/recommendations/management/commands/backfill_opportunity_reviews.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
from django.core.management.base import BaseCommand

from apps.recommendations.models import AIRecommendation


SOURCE_TYPES = {"pricing_strategy", "qualification", "prepare_proposal", "schedule_call"}


class Command(BaseCommand):
    help = "Genera opportunity_review cuando ya existan señales comerciales claras en recomendaciones previas."

    def handle(self, *args, **options):
        created = 0

        source_recommendations = AIRecommendation.objects.filter(
            recommendation_type__in=SOURCE_TYPES
        ).order_by("id")

        for rec in source_recommendations:
            already_exists = AIRecommendation.objects.filter(
                scope_type=rec.scope_type,
                scope_id=rec.scope_id,
                recommendation_type="opportunity_review",
            ).exists()

            if already_exists:
                continue

            AIRecommendation.objects.create(
                scope_type=rec.scope_type,
                scope_id=rec.scope_id,
                recommendation_type="opportunity_review",
                recommendation_text=(
                    f"Revisar oportunidad comercial: señal derivada de '{rec.recommendation_type}'."
                ),
                confidence=max(float(rec.confidence or 0.70), 0.75),
                status="new",
            )
            created += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f"CREATED scope={rec.scope_type}:{rec.scope_id} from recommendation={rec.id}"
                )
            )

        self.stdout.write("")
        self.stdout.write(f"created={created}")
