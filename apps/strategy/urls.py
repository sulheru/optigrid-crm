# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/strategy/urls.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
from django.urls import path

from .views import StrategyChatView

app_name = "strategy"

urlpatterns = [
    path("chat/", StrategyChatView.as_view(), name="chat"),
]
