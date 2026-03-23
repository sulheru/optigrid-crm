# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/recommendations/urls.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.

from django.urls import path

from . import views
from .views_simulation import simulate_recommendation


urlpatterns = [
    # List
    path("", views.recommendation_list),

    # Core actions
    path("<int:pk>/create-task/", views.recommendation_create_task),
    path("<int:pk>/dismiss/", views.recommendation_dismiss),
    path("<int:pk>/promote-opportunity/", views.recommendation_promote_opportunity),

    # Execute
    path("<int:pk>/execute/", views.execute_recommendation, name="execute_recommendation"),
    path("<int:pk>/execute-followup/", views.execute_followup, name="execute_followup"),
    path("<int:pk>/execute-contact-strategy/", views.execute_contact_strategy, name="execute_contact_strategy"),
    path("<int:pk>/execute-reply-strategy/", views.execute_reply_strategy, name="execute_reply_strategy"),

    # Simulation (Decision Cockpit)
    path("simulate/<int:recommendation_id>/", simulate_recommendation, name="simulate_recommendation"),
]
