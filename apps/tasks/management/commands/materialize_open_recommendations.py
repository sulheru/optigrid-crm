# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/tasks/management/commands/materialize_open_recommendations.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
from django.core.management.base import BaseCommand

from apps.recommendations.models import AIRecommendation
from apps.tasks.models import CRMTask
from apps.tasks.services.materialize import materialize_recommendation_as_task


class Command(BaseCommand):
    help = "Materializa recomendaciones abiertas en tareas si todavía no tienen task asociada."

    def add_arguments(self, parser):
        parser.add_argument(
            "--types",
            nargs="*",
            default=[],
            help="Filtrar por recommendation_type. Ejemplo: --types opportunity_review qualification",
        )

    def handle(self, *args, **options):
        recommendation_types = options.get("types") or []

        recommendations = AIRecommendation.objects.all().order_by("id")

        if recommendation_types:
            recommendations = recommendations.filter(recommendation_type__in=recommendation_types)

        created = 0
        reused = 0
        scanned = 0

        for recommendation in recommendations:
            scanned += 1

            existing = CRMTask.objects.filter(source_recommendation=recommendation).first()
            if existing:
                reused += 1
                self.stdout.write(
                    f"REUSED recommendation={recommendation.pk} task={existing.pk} type={recommendation.recommendation_type}"
                )
                continue

            task = materialize_recommendation_as_task(recommendation)
            created += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f"CREATED recommendation={recommendation.pk} task={task.pk} type={recommendation.recommendation_type} -> {task.task_type}"
                )
            )

        self.stdout.write("")
        self.stdout.write(f"scanned={scanned}")
        self.stdout.write(f"created={created}")
        self.stdout.write(f"reused={reused}")
