# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/opportunities/services/promote.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
from apps.opportunities.models import Opportunity
from apps.tasks.models import CRMTask


PROMOTABLE_TASK_TYPES = {
    "schedule_call",
    "prepare_proposal",
    "follow_up",
}


def promote_task_to_opportunity(task: CRMTask) -> Opportunity:
    existing = task.opportunities.first()
    if existing:
        return existing

    stage = "new"
    if task.task_type == "prepare_proposal":
        stage = "proposal"
    elif task.task_type == "schedule_call":
        stage = "qualified"

    opportunity = Opportunity.objects.create(
        source_task=task,
        title=task.title,
        company_name="",
        stage=stage,
        confidence=0.6,
        summary=task.description or "",
    )
    return opportunity
