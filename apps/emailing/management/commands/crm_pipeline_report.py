# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/emailing/management/commands/crm_pipeline_report.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db.models import Case, CharField, Count, Value, When

from apps.emailing.models import EmailMessage
from apps.facts.models import FactRecord
from apps.inferences.models import InferenceRecord
from apps.updates.models import CRMUpdateProposal
from apps.recommendations.models import AIRecommendation
from apps.tasks.models import CRMTask
from apps.opportunities.models import Opportunity


def _field_names(model) -> set[str]:
    return {f.name for f in model._meta.fields}


def _print_section(title: str):
    print("")
    print(f"=== {title} ===")


def _print_kv(label: str, value):
    print(f"{label}: {value}")


def _print_grouped_counts(queryset, field_name: str, label: str):
    rows = (
        queryset.values(field_name)
        .annotate(total=Count("id"))
        .order_by(field_name)
    )
    _print_section(label)
    if not rows:
        print("—")
        return

    for row in rows:
        key = row[field_name] if row[field_name] not in (None, "") else "—"
        print(f"{key}: {row['total']}")


def _recommendation_confidence_buckets():
    field_names = _field_names(AIRecommendation)
    if "confidence" not in field_names:
        return None

    return (
        AIRecommendation.objects.annotate(
            confidence_bucket=Case(
                When(confidence__lt=0.30, then=Value("0.00-0.29 low")),
                When(confidence__lt=0.50, then=Value("0.30-0.49 weak")),
                When(confidence__lt=0.70, then=Value("0.50-0.69 medium")),
                When(confidence__lt=0.85, then=Value("0.70-0.84 good")),
                default=Value("0.85-1.00 high"),
                output_field=CharField(),
            )
        )
        .values("confidence_bucket")
        .annotate(total=Count("id"))
        .order_by("confidence_bucket")
    )


class Command(BaseCommand):
    help = "Muestra auditoría del pipeline CRM IA-first."

    def handle(self, *args, **options):
        _print_section("TOTALS")
        _print_kv("emails", EmailMessage.objects.count())
        _print_kv("facts", FactRecord.objects.count())
        _print_kv("inferences", InferenceRecord.objects.count())
        _print_kv("proposals", CRMUpdateProposal.objects.count())
        _print_kv("recommendations", AIRecommendation.objects.count())
        _print_kv("tasks", CRMTask.objects.count())
        _print_kv("opportunities", Opportunity.objects.count())

        rec_fields = _field_names(AIRecommendation)
        task_fields = _field_names(CRMTask)
        opp_fields = _field_names(Opportunity)

        if "status" in rec_fields:
            _print_grouped_counts(
                AIRecommendation.objects.all(),
                "status",
                "RECOMMENDATIONS BY STATUS",
            )

        if "recommendation_type" in rec_fields:
            _print_grouped_counts(
                AIRecommendation.objects.all(),
                "recommendation_type",
                "RECOMMENDATIONS BY TYPE",
            )

        confidence_rows = _recommendation_confidence_buckets()
        if confidence_rows is not None:
            _print_section("RECOMMENDATIONS BY CONFIDENCE")
            has_rows = False
            for row in confidence_rows:
                has_rows = True
                print(f"{row['confidence_bucket']}: {row['total']}")
            if not has_rows:
                print("—")

        if "status" in task_fields:
            _print_grouped_counts(
                CRMTask.objects.all(),
                "status",
                "TASKS BY STATUS",
            )

        if "task_type" in task_fields:
            _print_grouped_counts(
                CRMTask.objects.all(),
                "task_type",
                "TASKS BY TYPE",
            )

        if "priority" in task_fields:
            _print_grouped_counts(
                CRMTask.objects.all(),
                "priority",
                "TASKS BY PRIORITY",
            )

        if "stage" in opp_fields:
            _print_grouped_counts(
                Opportunity.objects.all(),
                "stage",
                "OPPORTUNITIES BY STAGE",
            )
