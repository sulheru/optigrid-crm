from __future__ import annotations

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError

from apps.opportunities.services.context_builder import build_opportunity_analysis_context
from apps.opportunities.services.opportunity_analyzer import analyze_opportunity_context


def _build_recommendation_text(base_text: str, rationale: str | None = None) -> str:
    base_text = (base_text or "").strip()
    rationale = (rationale or "").strip()

    if not rationale:
        return base_text

    return f"{base_text}\n\nRationale: {rationale}"


class Command(BaseCommand):
    help = "Analiza una Opportunity existente y genera nuevas AIRecommendation."

    def add_arguments(self, parser):
        parser.add_argument("opportunity_id", type=int)

    def handle(self, *args, **options):
        Opportunity = apps.get_model("opportunities", "Opportunity")
        AIRecommendation = apps.get_model("recommendations", "AIRecommendation")

        opportunity_id = options["opportunity_id"]
        opportunity = Opportunity.objects.filter(pk=opportunity_id).first()
        if opportunity is None:
            raise CommandError(f"Opportunity {opportunity_id} no existe.")

        self.stdout.write(self.style.NOTICE(f"Analyzing opportunity {opportunity_id}..."))

        context = build_opportunity_analysis_context(opportunity)
        context_dict = context.to_dict()

        self.stdout.write("Context summary:")
        self.stdout.write(context.summary_text or "(sin resumen)")

        generated = analyze_opportunity_context(context_dict)

        self.stdout.write("")
        self.stdout.write("Context counts:")
        self.stdout.write(f"- inferences: {len(context.inferences)}")
        self.stdout.write(f"- facts: {len(context.facts)}")
        self.stdout.write(f"- emails: {len(context.emails)}")
        self.stdout.write(f"- active_recommendations: {len(context.active_recommendations)}")
        self.stdout.write(f"- open_tasks: {len(context.open_tasks)}")

        if not generated:
            self.stdout.write(self.style.WARNING("No se generaron recomendaciones."))
            return

        created_count = 0
        reused_count = 0

        for item in generated:
            recommendation_type = item["recommendation_type"]
            recommendation_text = item["recommendation_text"]
            rationale = item.get("rationale")
            confidence = item["confidence"]

            final_text = _build_recommendation_text(
                base_text=recommendation_text,
                rationale=rationale,
            )

            existing = AIRecommendation.objects.filter(
                scope_type="opportunity",
                scope_id=opportunity.id,
                recommendation_type=recommendation_type,
                recommendation_text=final_text,
            ).exclude(status="dismissed").first()

            if existing is not None:
                reused_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"REUSED recommendation={existing.id} type={recommendation_type}"
                    )
                )
                continue

            recommendation = AIRecommendation.objects.create(
                scope_type="opportunity",
                scope_id=opportunity.id,
                recommendation_type=recommendation_type,
                recommendation_text=final_text,
                confidence=confidence,
                status="new",
            )
            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f"CREATED recommendation={recommendation.id} type={recommendation_type}"
                )
            )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Done. created={created_count} reused={reused_count}"
            )
        )
