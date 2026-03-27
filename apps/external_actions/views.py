from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404

from apps.external_actions.models import ExternalActionIntent
from apps.external_actions.services.approval import approve_external_action_intent


def approve_intent(request, pk):
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid method")

    intent = get_object_or_404(ExternalActionIntent, pk=pk)

    if not request.user.is_authenticated:
        return HttpResponseBadRequest("Authentication required")

    approve_external_action_intent(intent, request.user)

    return JsonResponse({
        "status": "approved",
        "intent_id": intent.pk,
    })
