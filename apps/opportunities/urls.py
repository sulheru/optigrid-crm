from django.urls import path

from apps.opportunities.views_prioritized import (
    opportunity_tasks_view,
    prioritized_opportunities_view,
)

urlpatterns = [
    path("prioritized/", prioritized_opportunities_view, name="prioritized_opportunities"),
    path("<int:pk>/tasks/", opportunity_tasks_view, name="opportunity_tasks"),
]
