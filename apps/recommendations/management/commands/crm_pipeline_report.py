from django.core.management.base import BaseCommand
from django.db.models import Count

from apps.emailing.models import EmailMessage
from apps.facts.models import FactRecord
from apps.inferences.models import InferenceRecord
from apps.updates.models import CRMUpdateProposal
from apps.recommendations.models import AIRecommendation
from apps.tasks.models import CRMTask
from apps.opportunities.models import Opportunity


class Command(BaseCommand):
    help = "Muestra un resumen compacto del pipeline IA-first del CRM."

    def handle(self, *args, **kwargs):
        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_HEADING("CRM PIPELINE REPORT"))
        self.stdout.write("")

        self.stdout.write(f"emails={EmailMessage.objects.count()}")
        self.stdout.write(f"facts={FactRecord.objects.count()}")
        self.stdout.write(f"inferences={InferenceRecord.objects.count()}")
        self.stdout.write(f"proposals={CRMUpdateProposal.objects.count()}")
        self.stdout.write(f"recommendations={AIRecommendation.objects.count()}")
        self.stdout.write(f"tasks={CRMTask.objects.count()}")
        self.stdout.write(f"opportunities={Opportunity.objects.count()}")

        self.stdout.write("")
        self.stdout.write("recommendation_status:")

        rec_rows = (
            AIRecommendation.objects
            .values("status")
            .annotate(total=Count("id"))
            .order_by("status")
        )
        if rec_rows:
            for row in rec_rows:
                self.stdout.write(f"- {row['status']}={row['total']}")
        else:
            self.stdout.write("- no data")

        self.stdout.write("")
        self.stdout.write("recommendation_type:")

        rec_type_rows = (
            AIRecommendation.objects
            .values("recommendation_type")
            .annotate(total=Count("id"))
            .order_by("recommendation_type")
        )
        if rec_type_rows:
            for row in rec_type_rows:
                self.stdout.write(f"- {row['recommendation_type']}={row['total']}")
        else:
            self.stdout.write("- no data")

        self.stdout.write("")
        self.stdout.write("task_status:")

        task_rows = (
            CRMTask.objects
            .values("status")
            .annotate(total=Count("id"))
            .order_by("status")
        )
        if task_rows:
            for row in task_rows:
                self.stdout.write(f"- {row['status']}={row['total']}")
        else:
            self.stdout.write("- no data")

        self.stdout.write("")
        self.stdout.write("task_type:")

        task_type_rows = (
            CRMTask.objects
            .values("task_type")
            .annotate(total=Count("id"))
            .order_by("task_type")
        )
        if task_type_rows:
            for row in task_type_rows:
                self.stdout.write(f"- {row['task_type']}={row['total']}")
        else:
            self.stdout.write("- no data")

        self.stdout.write("")
        self.stdout.write("opportunity_fields:")

        opportunity_field_names = {f.name for f in Opportunity._meta.fields}

        if "stage" in opportunity_field_names:
            stage_rows = (
                Opportunity.objects
                .values("stage")
                .annotate(total=Count("id"))
                .order_by("stage")
            )
            self.stdout.write("stage:")
            if stage_rows:
                for row in stage_rows:
                    self.stdout.write(f"- {row['stage']}={row['total']}")
            else:
                self.stdout.write("- no data")
        elif "status" in opportunity_field_names:
            status_rows = (
                Opportunity.objects
                .values("status")
                .annotate(total=Count("id"))
                .order_by("status")
            )
            self.stdout.write("status:")
            if status_rows:
                for row in status_rows:
                    self.stdout.write(f"- {row['status']}={row['total']}")
            else:
                self.stdout.write("- no data")
        else:
            self.stdout.write("- stage/status field not found")

        self.stdout.write("")
