from django.core.management.base import BaseCommand

from apps.opportunities.models import Opportunity
from apps.opportunities.services.opportunity_analyzer import analyze_opportunity_core


class Command(BaseCommand):
    help = "Analyze all open opportunities"

    def handle(self, *args, **options):
        open_opportunities = Opportunity.objects.exclude(
            stage__in=["closed", "lost"]
        ).order_by("id")

        total = open_opportunities.count()

        self.stdout.write(f"Analyzing {total} open opportunities...\n")

        total_created = 0
        total_reused = 0

        for opp in open_opportunities:
            created, reused = analyze_opportunity_core(opp)

            total_created += created
            total_reused += reused

            self.stdout.write(f"Opportunity {opp.id}")
            self.stdout.write(f"created: {created}")
            self.stdout.write(f"reused: {reused}\n")

        self.stdout.write("Summary:\n")
        self.stdout.write(f"opportunities_analyzed: {total}")
        self.stdout.write(f"recommendations_created: {total_created}")
        self.stdout.write(f"recommendations_reused: {total_reused}")
