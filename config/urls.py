# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/config/urls.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),

    # Dashboard mock en raíz
    path("", TemplateView.as_view(template_name="dashboard/home.html"), name="home"),

    # Lead research
    path("", include("apps.lead_research.urls")),

    # Strategy
    path("strategy/", include("apps.strategy.urls")),

    # Emailing
    path("", include("apps.emailing.urls")),

    # Recommendations
    path("recommendations/", include("apps.recommendations.urls")),

    # Otros módulos
    path("tasks/", include("apps.tasks.urls")),
    path("opportunities/", include("apps.opportunities.urls")),
]
