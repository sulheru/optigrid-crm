# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/lead_research/tasks.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
import logging

from celery import shared_task

from apps.lead_research.services.signal_discovery import SignalDiscoveryService

logger = logging.getLogger(__name__)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def run_lead_signal_discovery(self):
    service = SignalDiscoveryService()
    result = service.run()
    payload = {
        "queries": result.queries,
        "processed": result.processed,
        "created": result.created,
        "updated": result.updated,
        "skipped_existing_company": result.skipped_existing_company,
        "skipped_existing_suggestion": result.skipped_existing_suggestion,
        "skipped_dismissed": result.skipped_dismissed,
        "validation_errors": result.validation_errors,
    }
    logger.info("lead_research.discovery.task_completed payload=%s", payload)
    return payload
