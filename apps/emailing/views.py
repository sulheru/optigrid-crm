from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.emailing.models import InboundEmail, OutboundEmail
from apps.emailing.services.inbound_analysis_service import analyze_inbound_email
from apps.emailing.services.outbound_sender import (
    send_all_approved_outbound_emails,
    send_outbound_email,
)
from apps.emailing.services.reply_generator import generate_followup_draft_from_inbound


def outbox_view(request):
    status = request.GET.get("status", "all")
    email_type = request.GET.get("type", "all")

    emails = OutboundEmail.objects.all().select_related("opportunity", "source_inbound")

    if status != "all":
        emails = emails.filter(status=status)

    if email_type != "all":
        emails = emails.filter(email_type=email_type)

    emails = emails.order_by("-created_at")[:200]

    base_qs = OutboundEmail.objects.all()

    context = {
        "emails": emails,
        "status": status,
        "email_type": email_type,
        "counts": {
            "all": base_qs.count(),
            "draft": base_qs.filter(status=OutboundEmail.STATUS_DRAFT).count(),
            "approved": base_qs.filter(status=OutboundEmail.STATUS_APPROVED).count(),
            "sent": base_qs.filter(status=OutboundEmail.STATUS_SENT).count(),
            "failed": base_qs.filter(status=OutboundEmail.STATUS_FAILED).count(),
            "first_contact": base_qs.filter(email_type=OutboundEmail.TYPE_FIRST_CONTACT).count(),
            "followup": base_qs.filter(email_type=OutboundEmail.TYPE_FOLLOWUP).count(),
        },
    }
    return render(request, "emailing/outbox.html", context)


def approve_email(request, pk):
    email = get_object_or_404(OutboundEmail, pk=pk)
    email.status = OutboundEmail.STATUS_APPROVED
    email.approved_at = timezone.now()
    email.failed_at = None
    email.failure_reason = ""
    email.save(update_fields=["status", "approved_at", "failed_at", "failure_reason", "updated_at"])
    return redirect(request.META.get("HTTP_REFERER", "/outbox/"))


def back_to_draft(request, pk):
    email = get_object_or_404(OutboundEmail, pk=pk)
    email.status = OutboundEmail.STATUS_DRAFT
    email.approved_at = None
    email.save(update_fields=["status", "approved_at", "updated_at"])
    return redirect(request.META.get("HTTP_REFERER", "/outbox/"))


def send_email(request, pk):
    email = get_object_or_404(OutboundEmail, pk=pk)
    send_outbound_email(email)
    return redirect(request.META.get("HTTP_REFERER", "/outbox/"))


def send_all(request):
    email_type = request.GET.get("type")
    if email_type == "all":
        email_type = None
    send_all_approved_outbound_emails(email_type=email_type)
    return redirect(request.META.get("HTTP_REFERER", "/outbox/"))


@require_POST
def bulk_action(request):
    action = request.POST.get("action", "").strip()
    selected_ids = request.POST.getlist("selected_ids")
    status = request.POST.get("status", "all")
    email_type = request.POST.get("type", "all")

    qs = OutboundEmail.objects.filter(id__in=selected_ids)

    if action == "approve":
        qs.update(
            status=OutboundEmail.STATUS_APPROVED,
            approved_at=timezone.now(),
            failed_at=None,
            failure_reason="",
        )
    elif action == "back_to_draft":
        qs.update(
            status=OutboundEmail.STATUS_DRAFT,
            approved_at=None,
        )
    elif action == "send":
        for email in qs.order_by("created_at"):
            send_outbound_email(email)

    return redirect(f"/outbox/?status={status}&type={email_type}")


def inbox_view(request):
    status = request.GET.get("status", "all")
    reply_type = request.GET.get("reply_type", "all")

    emails = InboundEmail.objects.all().select_related(
        "opportunity",
        "source_outbound",
        "ai_interpretation",
    ).prefetch_related("ai_decisions")

    if status != "all":
        emails = emails.filter(status=status)

    if reply_type != "all":
        emails = emails.filter(reply_type=reply_type)

    emails = list(emails.order_by("-received_at", "-created_at")[:200])

    for email in emails:
        if not hasattr(email, "ai_interpretation"):
            analyze_inbound_email(email)
        elif not email.ai_decisions.filter(status="suggested").exists():
            analyze_inbound_email(email)

    emails = list(
        InboundEmail.objects.all()
        .select_related("opportunity", "source_outbound", "ai_interpretation")
        .prefetch_related("ai_decisions")
        .filter(id__in=[e.id for e in emails])
        .order_by("-received_at", "-created_at")
    )

    for email in emails:
        suggested_decision = None
        for decision in email.ai_decisions.all():
            if decision.status == "suggested":
                suggested_decision = decision
                break
        email.suggested_decision = suggested_decision

    base_qs = InboundEmail.objects.all()

    context = {
        "emails": emails,
        "status": status,
        "reply_type": reply_type,
        "counts": {
            "all": base_qs.count(),
            "new": base_qs.filter(status=InboundEmail.STATUS_NEW).count(),
            "reviewed": base_qs.filter(status=InboundEmail.STATUS_REVIEWED).count(),
            "linked": base_qs.filter(status=InboundEmail.STATUS_LINKED).count(),
            "interested": base_qs.filter(reply_type=InboundEmail.REPLY_INTERESTED).count(),
            "needs_info": base_qs.filter(reply_type=InboundEmail.REPLY_NEEDS_INFO).count(),
            "not_now": base_qs.filter(reply_type=InboundEmail.REPLY_NOT_NOW).count(),
            "not_interested": base_qs.filter(reply_type=InboundEmail.REPLY_NOT_INTERESTED).count(),
            "unclear": base_qs.filter(reply_type=InboundEmail.REPLY_UNCLEAR).count(),
        },
    }
    return render(request, "emailing/inbox.html", context)


def mark_inbound_reviewed(request, pk):
    email = get_object_or_404(InboundEmail, pk=pk)
    email.status = InboundEmail.STATUS_REVIEWED
    email.save(update_fields=["status"])
    return redirect(request.META.get("HTTP_REFERER", "/inbox/"))


def mark_inbound_linked(request, pk):
    email = get_object_or_404(InboundEmail, pk=pk)
    email.status = InboundEmail.STATUS_LINKED
    email.save(update_fields=["status"])
    return redirect(request.META.get("HTTP_REFERER", "/inbox/"))


def generate_reply_draft(request, pk):
    email = get_object_or_404(InboundEmail, pk=pk)
    generate_followup_draft_from_inbound(email)
    return redirect("/outbox/?type=followup")
