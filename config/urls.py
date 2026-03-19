from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),

    # Home temporal estable
    path("", RedirectView.as_view(url="/leads/", permanent=False)),

    # Lead research
    path("", include("apps.lead_research.urls")),

    # Strategy
    path("strategy/", include("apps.strategy.urls")),

    # Outbox nuevo
    path("", include("apps.emailing.urls")),

    # Módulos ya existentes con sus propias URLs
    path("tasks/", include("apps.tasks.urls")),
    path("opportunities/", include("apps.opportunities.urls")),
]
