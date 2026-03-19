from django.urls import path
from . import views

urlpatterns = [
    path("leads/", views.lead_list_view, name="lead_list"),
    path("leads/<int:pk>/approve/", views.approve_lead, name="lead_approve"),
    path("leads/<int:pk>/dismiss/", views.dismiss_lead, name="lead_dismiss"),
    path("leads/<int:pk>/reopen/", views.reopen_lead, name="lead_reopen"),
]
