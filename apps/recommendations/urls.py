from django.urls import path

from . import views

urlpatterns = [
    path("", views.recommendation_list),
    path("<int:pk>/create-task/", views.recommendation_create_task),
    path("<int:pk>/dismiss/", views.recommendation_dismiss),
    path("<int:pk>/promote-opportunity/", views.recommendation_promote_opportunity),
    path("<int:pk>/execute-followup/", views.execute_followup, name="execute_followup"),
]
