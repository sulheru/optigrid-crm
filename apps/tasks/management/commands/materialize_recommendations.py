# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/tasks/management/commands/materialize_recommendations.py
from django.core.management.base import BaseCommand

from apps.recommendations.models import AIRecommendation
from apps.tasks.services.materialize import materialize_recommendation_as_task


class Command(BaseCommand):
    help = "Convierte recomendaciones IA en tareas CRM"

    def handle(self, *args, **options):
        recommendations = AIRecommendation.objects.all().order_by("id")
        created = 0
        reused = 0

        for recommendation in recommendations:
            before_exists = recommendation.tasks.exists()
            task = materialize_recommendation_as_task(recommendation)
            if before_exists:
                reused += 1
                self.stdout.write(f"REUSED task={task.id} recommendation={recommendation.id}")
            else:
                created += 1
                self.stdout.write(f"CREATED task={task.id} recommendation={recommendation.id}")

        self.stdout.write(self.style.SUCCESS(
            f"Done. created={created} reused={reused}"
        ))
