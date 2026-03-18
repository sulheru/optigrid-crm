from django.core.management.base import BaseCommand

from apps.opportunities.models import Opportunity
from apps.opportunities.services.opportunity_analyzer import analyze_opportunity


class Command(BaseCommand):
    help = "Analyze all open opportunities"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force analysis even if the opportunity was analyzed recently.",
        )

    def handle(self, *args, **options):
        force = options["force"]

        open_opportunities = Opportunity.objects.exclude(
            stage__in=["won", "lost"]
        ).order_by("id")

        total = open_opportunities.count()

        self.stdout.write(f"Analyzing {total} open opportunities...\n")

        total_analyzed = 0
        total_skipped = 0
        total_created = 0
        total_reused = 0
        total_tasks_created = 0
        total_tasks_reused = 0

        for opp in open_opportunities:
            result = analyze_opportunity(opp, force=force)

            if result.analyzed:
                total_analyzed += 1
                total_created += result.recommendations_created
                total_reused += result.recommendations_reused
                total_tasks_created += result.tasks_created
                total_tasks_reused += result.tasks_reused
            else:
                total_skipped += 1

            self.stdout.write(f"Opportunity {opp.id}")
            self.stdout.write(f"analyzed: {result.analyzed}")
            self.stdout.write(f"skipped_reason: {result.skipped_reason}")
            self.stdout.write(f"score: {result.relevance_score}")
            self.stdout.write(f"priority: {result.priority_bucket}")
            self.stdout.write(f"risk_flags: {', '.join(result.risk_flags) or '-'}")
            self.stdout.write(f"next_actions: {', '.join(result.next_actions) or '-'}")
            self.stdout.write(f"recommendations_created: {result.recommendations_created}")
            self.stdout.write(f"recommendations_reused: {result.recommendations_reused}")
            self.stdout.write(f"tasks_created: {result.tasks_created}")
            self.stdout.write(f"tasks_reused: {result.tasks_reused}\n")

        self.stdout.write("Summary:\n")
        self.stdout.write(f"opportunities_total: {total}")
        self.stdout.write(f"opportunities_analyzed: {total_analyzed}")
        self.stdout.write(f"opportunities_skipped: {total_skipped}")
        self.stdout.write(f"recommendations_created: {total_created}")
        self.stdout.write(f"recommendations_reused: {total_reused}")
        self.stdout.write(f"tasks_created: {total_tasks_created}")
        self.stdout.write(f"tasks_reused: {total_tasks_reused}")
