from django.core.management.base import BaseCommand
from apps.opportunities.models import Opportunity
from apps.opportunities.services.opportunity_analyzer import analyze_opportunity_core


class Command(BaseCommand):
    help = "Analyze a single opportunity"

    def add_arguments(self, parser):
        parser.add_argument("opportunity_id", type=int)

    def handle(self, *args, **options):
        opportunity_id = options["opportunity_id"]

        try:
            opportunity = Opportunity.objects.get(id=opportunity_id)
        except Opportunity.DoesNotExist:
            self.stdout.write(self.style.ERROR("Opportunity not found"))
            return

        created, reused = analyze_opportunity_core(opportunity)

        self.stdout.write(self.style.SUCCESS(f"Opportunity {opportunity.id} analyzed"))
        self.stdout.write(f"created: {created}")
        self.stdout.write(f"reused: {reused}")
