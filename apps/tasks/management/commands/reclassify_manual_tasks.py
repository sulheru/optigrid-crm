# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/tasks/management/commands/reclassify_manual_tasks.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
from django.core.management.base import BaseCommand

from apps.tasks.models import CRMTask
from apps.recommendations.models import AIRecommendation


RECOMMENDATION_TO_TASK_TYPE = {
    "opportunity_review": "opportunity_review",
    "qualification": "qualification_review",
    "pricing_strategy": "pricing_review",
}


class Command(BaseCommand):
    help = "Reclasifica tareas review_manually a tipos más específicos cuando sea posible."

    def handle(self, *args, **options):
        updated = 0
        scanned = 0

        tasks = CRMTask.objects.filter(task_type="review_manually")

        for task in tasks:
            scanned += 1

            recommendation = None

            if hasattr(task, "source_recommendation_id") and task.source_recommendation_id:
                recommendation = AIRecommendation.objects.filter(pk=task.source_recommendation_id).first()

            if recommendation is None and hasattr(task, "scope_type") and hasattr(task, "scope_id"):
                recommendation = AIRecommendation.objects.filter(
                    scope_type=getattr(task, "scope_type", None),
                    scope_id=getattr(task, "scope_id", None),
                ).order_by("-id").first()

            if recommendation is None:
                continue

            new_type = RECOMMENDATION_TO_TASK_TYPE.get(recommendation.recommendation_type)
            if not new_type:
                continue

            task.task_type = new_type
            task.save(update_fields=["task_type"])
            updated += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f"UPDATED task={task.pk} recommendation={recommendation.pk} -> {new_type}"
                )
            )

        self.stdout.write("")
        self.stdout.write(f"scanned={scanned}")
        self.stdout.write(f"updated={updated}")
