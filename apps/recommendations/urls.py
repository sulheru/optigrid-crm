from django.urls import path

from . import views

urlpatterns = [
    path("", views.recommendation_list),
    path("<int:pk>/create-task/", views.recommendation_create_task),
    path("<int:pk>/dismiss/", views.recommendation_dismiss),
    path("<int:pk>/promote-opportunity/", views.recommendation_promote_opportunity),
    path("<int:pk>/execute/", views.execute_recommendation, name="execute_recommendation"),
    path("<int:pk>/execute-followup/", views.execute_followup, name="execute_followup"),
    path("<int:pk>/execute-contact-strategy/", views.execute_contact_strategy, name="execute_contact_strategy"),
    path("<int:pk>/execute-reply-strategy/", views.execute_reply_strategy, name="execute_reply_strategy"),
]
