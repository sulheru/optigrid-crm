from django.urls import path

from .views import StrategyChatView

app_name = "strategy"

urlpatterns = [
    path("chat/", StrategyChatView.as_view(), name="chat"),
]
