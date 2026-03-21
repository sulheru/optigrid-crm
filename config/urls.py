from django.contrib import admin
from django.urls import include, path

from apps.dashboard_views import dashboard_home_view

urlpatterns = [
    path("admin/", admin.site.urls),

    # Dashboard real en raíz
    path("", dashboard_home_view, name="home"),

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
