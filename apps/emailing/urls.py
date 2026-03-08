from django.urls import path

from .views import email_detail_view, email_list_view

app_name = "emailing"

urlpatterns = [
    path("", email_list_view, name="email_list"),
    path("<int:pk>/", email_detail_view, name="email_detail"),
]
