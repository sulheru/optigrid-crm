# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/opportunities/tasks.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
from __future__ import annotations

from celery import shared_task
from django.conf import settings

from apps.opportunities.models import Opportunity
from apps.opportunities.services.opportunity_analyzer import analyze_opportunity


@shared_task(name="apps.opportunities.tasks.analyze_open_opportunities_task")
def analyze_open_opportunities_task(force: bool = False) -> dict:
    if not getattr(settings, "OPPORTUNITY_ANALYSIS_ENABLED", True):
        return {
            "enabled": False,
            "analyzed": 0,
            "skipped": 0,
            "recommendations_created": 0,
            "recommendations_reused": 0,
            "prioritized_opportunities": [],
        }

    queryset = Opportunity.objects.exclude(stage__in=["won", "lost"]).order_by("id")

    batch_size = int(getattr(settings, "OPPORTUNITY_ANALYSIS_BATCH_SIZE", 50) or 50)
    total_candidates = queryset.count()
    analyzed = 0
    skipped = 0
    created = 0
    reused = 0
    prioritized: list[dict] = []

    for opportunity in queryset[:batch_size]:
        result = analyze_opportunity(opportunity, force=force)

        if result.analyzed:
            analyzed += 1
            created += result.recommendations_created
            reused += result.recommendations_reused
            prioritized.append(
                {
                    "opportunity_id": result.opportunity_id,
                    "relevance_score": result.relevance_score,
                    "priority_bucket": result.priority_bucket,
                    "risk_flags": result.risk_flags,
                    "next_actions": result.next_actions,
                }
            )
        else:
            skipped += 1

    prioritized.sort(
        key=lambda item: (item["relevance_score"], item["opportunity_id"]),
        reverse=True,
    )

    return {
        "enabled": True,
        "total_candidates": total_candidates,
        "batch_size": batch_size,
        "analyzed": analyzed,
        "skipped": skipped,
        "recommendations_created": created,
        "recommendations_reused": reused,
        "prioritized_opportunities": prioritized,
    }
