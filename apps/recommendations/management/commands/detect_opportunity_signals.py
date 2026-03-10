from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.emailing.models import EmailMessage
from apps.recommendations.opportunity_intelligence import (
    assess_source_for_opportunity,
    ensure_opportunity_review_recommendation,
)


class Command(BaseCommand):
    help = "Detecta señales comerciales y crea recomendaciones opportunity_review cuando proceda."

    def add_arguments(self, parser):
        parser.add_argument(
            "--source-id",
            type=int,
            default=None,
            help="Procesar solo un EmailMessage concreto por id.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Evalúa señales sin crear recomendaciones.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Limitar número de emails procesados.",
        )

    def handle(self, *args, **options):
        qs = EmailMessage.objects.all().order_by("id")
        source_id = options["source_id"]
        dry_run = options["dry_run"]
        limit = options["limit"]

        if source_id is not None:
            qs = qs.filter(id=source_id)

        if limit:
            qs = qs[:limit]

        processed = 0
        created = 0
        reused = 0
        skipped = 0

        for email in qs:
            processed += 1

            if dry_run:
                assessment = assess_source_for_opportunity("email_message", email.id)
                self.stdout.write(
                    f"EMAIL id={email.id} score={assessment.score} "
                    f"confidence={assessment.confidence} create={assessment.should_create} "
                    f"rationale={assessment.rationale}"
                )
                if assessment.should_create:
                    created += 1
                else:
                    skipped += 1
                continue

            recommendation, was_created, assessment = ensure_opportunity_review_recommendation(
                source_type="email_message",
                source_id=email.id,
            )

            if recommendation is None:
                skipped += 1
                self.stdout.write(
                    f"SKIPPED email={email.id} score={assessment.score} rationale={assessment.rationale}"
                )
                continue

            if was_created:
                created += 1
                self.stdout.write(
                    f"CREATED email={email.id} recommendation={recommendation.id} "
                    f"score={assessment.score} confidence={assessment.confidence}"
                )
            else:
                reused += 1
                self.stdout.write(
                    f"REUSED email={email.id} recommendation={recommendation.id} "
                    f"score={assessment.score} confidence={assessment.confidence}"
                )

        self.stdout.write("")
        self.stdout.write("=== OPPORTUNITY SIGNAL REPORT ===")
        self.stdout.write(f"processed={processed}")
        self.stdout.write(f"created={created}")
        self.stdout.write(f"reused={reused}")
        self.stdout.write(f"skipped={skipped}")
