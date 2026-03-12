from django.urls import path

from .views import list_opportunities, transition_opportunity_stage

app_name = "opportunities"

urlpatterns = [
    path("", list_opportunities, name="list"),
    path("<int:pk>/transition/", transition_opportunity_stage, name="transition"),
]
