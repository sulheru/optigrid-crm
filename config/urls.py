from django.contrib import admin
from django.urls import include, path

from apps.emailing.views import (
    dashboard_view,
    opportunities_list_view,
    recommendations_list_view,
    recommendation_create_task_view,
    recommendation_dismiss_view,
    task_set_status_view,
    tasks_list_view,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", dashboard_view, name="dashboard"),
    path("emails/", include(("apps.emailing.urls", "emailing"), namespace="emailing")),

    path("recommendations/", recommendations_list_view, name="recommendations"),
    path("recommendations/<int:pk>/create-task/", recommendation_create_task_view),
    path("recommendations/<int:pk>/dismiss/", recommendation_dismiss_view),

    path("tasks/", tasks_list_view, name="tasks"),
    path("tasks/<int:pk>/set-status/", task_set_status_view, name="task_set_status"),

    path("opportunities/", opportunities_list_view, name="opportunities"),
]
