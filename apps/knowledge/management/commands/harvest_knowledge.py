from django.core.management.base import BaseCommand

from apps.knowledge.services.generator import generate_knowledge_candidates


class Command(BaseCommand):
    help = "Extrae señal desde emails e intenta generar KnowledgeCandidates."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=200)
        parser.add_argument("--similarity-threshold", type=float, default=0.78)
        parser.add_argument("--min-cluster-size", type=int, default=2)

    def handle(self, *args, **options):
        result = generate_knowledge_candidates(
            limit=options["limit"],
            similarity_threshold=options["similarity_threshold"],
            min_cluster_size=options["min_cluster_size"],
        )
        self.stdout.write(
            self.style.SUCCESS(
                "Knowledge harvest completed "
                f"(signals={result['signals']}, created={result['created']}, reused={result['reused']})"
            )
        )
