from django.core.management.base import BaseCommand, CommandError

from apps.knowledge.models import KnowledgeCandidate
from apps.knowledge.services.promotion import accept_candidate, reject_candidate


class Command(BaseCommand):
    help = "Acepta o rechaza un KnowledgeCandidate."

    def add_arguments(self, parser):
        parser.add_argument("candidate_id", type=int)
        parser.add_argument("--accept", action="store_true")
        parser.add_argument("--reject", action="store_true")

    def handle(self, *args, **options):
        if options["accept"] == options["reject"]:
            raise CommandError("Debes indicar exactamente una acción: --accept o --reject")

        candidate = KnowledgeCandidate.objects.filter(pk=options["candidate_id"]).first()
        if not candidate:
            raise CommandError("KnowledgeCandidate no encontrado")

        if options["accept"]:
            promoted = accept_candidate(candidate)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Candidate {candidate.pk} accepted"
                    + (f" -> promoted to {promoted.__class__.__name__} #{promoted.pk}" if promoted else "")
                )
            )
            return

        reject_candidate(candidate)
        self.stdout.write(self.style.SUCCESS(f"Candidate {candidate.pk} rejected"))
