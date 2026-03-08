from django.urls import path
from . import views

app_name = "emailing"

urlpatterns = [
    path("emails/", views.email_list_view, name="email_list"),
    path("emails/<int:pk>/", views.email_detail_view, name="email_detail"),
]
