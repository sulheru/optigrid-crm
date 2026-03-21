# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/recommendations/urls.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
from django.urls import path
from . import views

urlpatterns = [
    path("", views.recommendation_list),
    path("<int:pk>/create-task/", views.recommendation_create_task),
    path("<int:pk>/dismiss/", views.recommendation_dismiss),
]
