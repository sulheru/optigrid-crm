from django.urls import path
from .views import approve_intent

urlpatterns = [
    path("<int:pk>/approve/", approve_intent, name="approve_intent"),
]
