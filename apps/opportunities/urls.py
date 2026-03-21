# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/opportunities/urls.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
from django.urls import path
from django.views.generic import RedirectView

from apps.opportunities.views_prioritized import (
    opportunity_set_stage_view,
    opportunity_tasks_view,
    prioritized_opportunities_view,
)

urlpatterns = [
    path(
        "",
        RedirectView.as_view(url="/opportunities/prioritized/", permanent=False),
        name="opportunities_home",
    ),
    path("prioritized/", prioritized_opportunities_view, name="prioritized_opportunities"),
    path("<int:pk>/tasks/", opportunity_tasks_view, name="opportunity_tasks"),
    path("<int:pk>/set-stage/", opportunity_set_stage_view, name="opportunity_set_stage"),
]
