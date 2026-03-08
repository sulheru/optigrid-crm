from django.contrib import admin
from django.urls import include, path

from apps.emailing.views import (
    dashboard_view,
    opportunities_list_view,
    recommendations_list_view,
    tasks_list_view,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", dashboard_view, name="dashboard"),
    path("emails/", include(("apps.emailing.urls", "emailing"), namespace="emailing")),
    path("recommendations/", recommendations_list_view, name="recommendations"),
    path("tasks/", tasks_list_view, name="tasks"),
    path("opportunities/", opportunities_list_view, name="opportunities"),
]
