from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.emailing.models import InboundDecision, InboundEmail, OutboundEmail
from apps.emailing.services.inbound_analysis_service import analyze_inbound_email
from apps.emailing.services.inbound_decision_apply_service import (
    apply_inbound_decision,
    dismiss_inbound_decision,
)
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


def _build_inbox_queryset():
    decisions_qs = (
        InboundDecision.objects
        .select_related("interpretation")
        .order_by("-created_at")
    )

    return (
        InboundEmail.objects
        .select_related(
            "opportunity",
            "source_outbound",
            "ai_interpretation",
        )
        .prefetch_related(
            Prefetch("ai_decisions", queryset=decisions_qs)
        )
    )


def _get_prefetched_decisions(email):
    return list(email.ai_decisions.all())


def _needs_inbound_analysis(email):
    interpretation = getattr(email, "ai_interpretation", None)
    decisions = _get_prefetched_decisions(email)
    has_suggested_decision = any(
        decision.status == InboundDecision.STATUS_SUGGESTED
        for decision in decisions
    )
    return interpretation is None or not has_suggested_decision


def _hydrate_inbox_email(email):
    decisions = _get_prefetched_decisions(email)

    suggested_decision = next(
        (decision for decision in decisions if decision.status == InboundDecision.STATUS_SUGGESTED),
        None,
    )
    latest_non_suggested_decision = decisions[0] if decisions else None
    latest_decision = suggested_decision or latest_non_suggested_decision

    decision_output = {}
    semantic_effect = {}
    explanation_preview = []

    if latest_decision:
        payload_json = latest_decision.payload_json or {}
        maybe_decision_output = payload_json.get("decision_output")

        if isinstance(maybe_decision_output, dict):
            decision_output = maybe_decision_output

        final_effect = decision_output.get("final_effect") or {}
        maybe_semantic_effect = final_effect.get("semantic_effect") or {}
        explanation = decision_output.get("explanation") or []

        if isinstance(maybe_semantic_effect, dict):
            semantic_effect = maybe_semantic_effect

        if isinstance(explanation, list):
            explanation_preview = explanation[:2]

    email.suggested_decision = suggested_decision
    email.latest_decision = latest_decision
    email.latest_decision_output = decision_output
    email.latest_semantic_effect = semantic_effect
    email.latest_explanation_preview = explanation_preview
    return email


def _matches_inbox_filters(email, *, decision_status, automation, priority, risk):
    decision = getattr(email, "latest_decision", None)

    if decision_status != "all":
        if not decision or decision.status != decision_status:
            return False

    if automation == "auto":
        if not decision or not decision.applied_automatically:
            return False
    elif automation == "manual":
        if not decision or decision.applied_automatically:
            return False

    if priority != "all":
        if not decision or decision.priority != priority:
            return False

    if risk == "with_risk":
        if not decision or not decision.risk_flags:
            return False
    elif risk == "without_risk":
        if not decision or decision.risk_flags:
            return False

    return True


def inbox_view(request):
    status = request.GET.get("status", "all")
    reply_type = request.GET.get("reply_type", "all")
    decision_status = request.GET.get("decision_status", "all")
    automation = request.GET.get("automation", "all")
    priority = request.GET.get("priority", "all")
    risk = request.GET.get("risk", "all")

    emails_qs = _build_inbox_queryset()

    if status != "all":
        emails_qs = emails_qs.filter(status=status)

    if reply_type != "all":
        emails_qs = emails_qs.filter(reply_type=reply_type)

    emails = list(emails_qs.order_by("-received_at", "-created_at")[:200])

    emails_requiring_analysis = [email for email in emails if _needs_inbound_analysis(email)]
    analyzed_ids = []

    for email in emails_requiring_analysis:
        analyze_inbound_email(email)
        analyzed_ids.append(email.id)

    if analyzed_ids:
        emails = list(
            _build_inbox_queryset()
            .filter(id__in=[email.id for email in emails])
            .order_by("-received_at", "-created_at")
        )

    hydrated_emails = []
    for email in emails:
        hydrated_email = _hydrate_inbox_email(email)
        if _matches_inbox_filters(
            hydrated_email,
            decision_status=decision_status,
            automation=automation,
            priority=priority,
            risk=risk,
        ):
            hydrated_emails.append(hydrated_email)

    base_qs = InboundEmail.objects.all()
    decisions_qs = InboundDecision.objects.all()

    context = {
        "emails": hydrated_emails,
        "status": status,
        "reply_type": reply_type,
        "decision_status": decision_status,
        "automation": automation,
        "priority": priority,
        "risk": risk,
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
            "auto_applied": decisions_qs.filter(applied_automatically=True).count(),
            "manual_decisions": decisions_qs.filter(applied_automatically=False).count(),
            "suggested": decisions_qs.filter(status=InboundDecision.STATUS_SUGGESTED).count(),
            "applied": decisions_qs.filter(status=InboundDecision.STATUS_APPLIED).count(),
            "dismissed": decisions_qs.filter(status=InboundDecision.STATUS_DISMISSED).count(),
            "high_priority": decisions_qs.filter(priority=InboundDecision.PRIORITY_HIGH).count(),
            "with_risk": decisions_qs.exclude(risk_flags=[]).count(),
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


@require_POST
def apply_decision(request, pk):
    email = get_object_or_404(InboundEmail, pk=pk)
    decision = email.ai_decisions.filter(status=InboundDecision.STATUS_SUGGESTED).first()

    if decision:
        apply_inbound_decision(decision)

    return redirect(request.META.get("HTTP_REFERER", "/inbox/"))


@require_POST
def dismiss_decision(request, pk):
    email = get_object_or_404(InboundEmail, pk=pk)
    decision = email.ai_decisions.filter(status=InboundDecision.STATUS_SUGGESTED).first()

    if decision:
        dismiss_inbound_decision(decision)

    return redirect(request.META.get("HTTP_REFERER", "/inbox/"))


@require_POST
def update_outbound_email(request, pk):
    email = get_object_or_404(OutboundEmail, pk=pk)

    if email.status != OutboundEmail.STATUS_DRAFT:
        return redirect(request.META.get("HTTP_REFERER", "/outbox/"))

    subject = request.POST.get("subject", "").strip()
    body = request.POST.get("body", "").strip()

    email.subject = subject
    email.body = body
    email.save(update_fields=["subject", "body", "updated_at"])

    return redirect(request.META.get("HTTP_REFERER", "/outbox/"))
