from django.core.management.base import BaseCommand

from apps.opportunities.services.promote import PROMOTABLE_TASK_TYPES, promote_task_to_opportunity
from apps.tasks.models import CRMTask


class Command(BaseCommand):
    help = "Promueve tareas CRM a oportunidades"

    def handle(self, *args, **options):
        tasks = CRMTask.objects.filter(task_type__in=PROMOTABLE_TASK_TYPES).order_by("id")
        created = 0
        reused = 0

        for task in tasks:
            before_exists = task.opportunities.exists()
            opp = promote_task_to_opportunity(task)
            if before_exists:
                reused += 1
                self.stdout.write(f"REUSED opportunity={opp.id} task={task.id}")
            else:
                created += 1
                self.stdout.write(f"CREATED opportunity={opp.id} task={task.id}")

        self.stdout.write(self.style.SUCCESS(
            f"Done. created={created} reused={reused}"
        ))
