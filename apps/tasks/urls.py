# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/tasks/urls.py
from django.urls import path

from .views import revoke_task, tasks_list_view

app_name = "tasks"

urlpatterns = [
    path("", tasks_list_view, name="list"),
    path("<int:task_id>/revoke/", revoke_task, name="revoke_task"),
]
