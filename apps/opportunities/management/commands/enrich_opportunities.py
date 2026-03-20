# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/opportunities/management/commands/enrich_opportunities.py
from django.core.management.base import BaseCommand

from apps.opportunities.models import Opportunity
from apps.recommendations.models import AIRecommendation
from apps.opportunities.services.enrichment import build_opportunity_defaults_from_recommendation


class Command(BaseCommand):
    help = "Enriquece opportunities existentes a partir de su source_recommendation cuando sea posible."

    def handle(self, *args, **options):
        scanned = 0
        updated = 0

        for opportunity in Opportunity.objects.all().order_by("id"):
            scanned += 1

            recommendation = getattr(opportunity, "source_recommendation", None)

            if recommendation is None and opportunity.source_inference_type and opportunity.source_inference_id:
                recommendation = AIRecommendation.objects.filter(
                    scope_type=opportunity.source_inference_type,
                    scope_id=opportunity.source_inference_id,
                    recommendation_type="opportunity_review",
                ).order_by("-id").first()

            if recommendation is None:
                continue

            defaults = build_opportunity_defaults_from_recommendation(recommendation)
            changed_fields = []

            if not opportunity.company_name and defaults.get("company_name"):
                opportunity.company_name = defaults["company_name"]
                changed_fields.append("company_name")

            if opportunity.estimated_value in (None, "") and defaults.get("estimated_value") is not None:
                opportunity.estimated_value = defaults["estimated_value"]
                changed_fields.append("estimated_value")

            if opportunity.confidence in (None, "") and defaults.get("confidence") is not None:
                opportunity.confidence = defaults["confidence"]
                changed_fields.append("confidence")

            if (not opportunity.summary) and defaults.get("summary"):
                opportunity.summary = defaults["summary"]
                changed_fields.append("summary")

            if changed_fields:
                opportunity.save(update_fields=changed_fields + ["updated_at"])
                updated += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"UPDATED opportunity={opportunity.pk} fields={','.join(changed_fields)}"
                    )
                )

        self.stdout.write("")
        self.stdout.write(f"scanned={scanned}")
        self.stdout.write(f"updated={updated}")
