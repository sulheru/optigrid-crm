#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PWD}"
STAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR="$PROJECT_ROOT/.refactor_backups/inbox_v2_$STAMP"

mkdir -p "$BACKUP_DIR"
mkdir -p apps/emailing/services
mkdir -p apps/emailing/templates/emailing

backup_file() {
  local f="$1"
  if [ -f "$f" ]; then
    mkdir -p "$BACKUP_DIR/$(dirname "$f")"
    cp "$f" "$BACKUP_DIR/$f"
  fi
}

backup_file "apps/emailing/views.py"
backup_file "apps/emailing/urls.py"
backup_file "apps/emailing/templates/emailing/inbox.html"
backup_file "apps/emailing/tests.py"

cat > apps/emailing/services/inbound_decision_apply_service.py << 'PY'
import logging

from django.db import transaction
from django.utils import timezone

from apps.emailing.models import InboundDecision, OutboundEmail
from apps.tasks.models import CRMTask

logger = logging.getLogger(__name__)


def _build_reply_subject(inbound):
    subject = (inbound.subject or "").strip()
    if not subject:
        return "Re:"
    if subject.lower().startswith("re:"):
        return subject
    return f"Re: {subject}"


def _build_reply_body(inbound, decision):
    summary = (decision.summary or "").strip()
    if summary:
        return (
            "Hola,\n\n"
            "Gracias por tu mensaje.\n\n"
            f"{summary}\n\n"
            "Quedo atento.\n"
        )

    if decision.action_type == InboundDecision.ACTION_SEND_INFORMATION:
        return (
            "Hola,\n\n"
            "Gracias por tu mensaje.\n\n"
            "Te comparto la información solicitada y quedo atento a cualquier duda.\n\n"
            "Un saludo.\n"
        )

    return (
        "Hola,\n\n"
        "Gracias por tu mensaje.\n\n"
        "Para poder avanzar, ¿podrías compartir un poco más de contexto?\n\n"
        "Un saludo.\n"
    )


def _advance_opportunity(opportunity):
    if not opportunity:
        return None

    transitions = {
        "new": "qualified",
        "qualified": "proposal",
        "proposal": "won",
    }

    previous_stage = opportunity.stage
    next_stage = transitions.get(previous_stage, previous_stage)

    opportunity.stage = next_stage
    opportunity.save(update_fields=["stage", "updated_at"])
    return next_stage


def _mark_opportunity_lost(opportunity):
    if not opportunity:
        return

    opportunity.stage = "lost"
    opportunity.save(update_fields=["stage", "updated_at"])


def _create_followup_task(inbound, decision):
    return CRMTask.objects.create(
        opportunity=inbound.opportunity,
        title=f"Follow-up for inbound #{inbound.id}",
        description=decision.summary or "Follow-up suggested by Inbox Intelligence",
        task_type="follow_up",
        status="open",
        priority="normal",
        source="auto",
        source_action=decision.action_type,
    )


def _create_reply_draft(inbound, decision):
    return OutboundEmail.objects.create(
        opportunity=inbound.opportunity,
        source_inbound=inbound,
        email_type=OutboundEmail.TYPE_FOLLOWUP,
        to_email=inbound.from_email,
        subject=_build_reply_subject(inbound),
        body=_build_reply_body(inbound, decision),
        status=OutboundEmail.STATUS_DRAFT,
        generated_by="ai",
    )


@transaction.atomic
def apply_inbound_decision(decision: InboundDecision):
    if decision.status != InboundDecision.STATUS_SUGGESTED:
        raise ValueError("Decision is not in suggested state")

    inbound = decision.inbound_email
    action = decision.action_type

    task = None
    outbound = None
    opportunity_stage = None

    logger.info(
        "Applying inbound decision %s for inbound %s with action %s",
        decision.id,
        inbound.id,
        action,
    )

    if action == InboundDecision.ACTION_ADVANCE_OPPORTUNITY:
        opportunity_stage = _advance_opportunity(inbound.opportunity)

    elif action == InboundDecision.ACTION_SCHEDULE_FOLLOWUP:
        task = _create_followup_task(inbound, decision)

    elif action in (
        InboundDecision.ACTION_SEND_INFORMATION,
        InboundDecision.ACTION_SEND_CLARIFICATION,
    ):
        outbound = _create_reply_draft(inbound, decision)

    elif action == InboundDecision.ACTION_MARK_LOST:
        _mark_opportunity_lost(inbound.opportunity)
        opportunity_stage = "lost"

    else:
        raise ValueError(f"Unsupported action_type: {action}")

    decision.status = InboundDecision.STATUS_APPLIED
    decision.applied_at = timezone.now()
    decision.save(update_fields=["status", "applied_at"])

    return {
        "decision_id": decision.id,
        "task_id": getattr(task, "id", None),
        "outbound_id": getattr(outbound, "id", None),
        "opportunity_stage": opportunity_stage,
    }


def dismiss_inbound_decision(decision: InboundDecision):
    if decision.status != InboundDecision.STATUS_SUGGESTED:
        raise ValueError("Only suggested decisions can be dismissed")

    logger.info(
        "Dismissing inbound decision %s for inbound %s",
        decision.id,
        decision.inbound_email_id,
    )

    decision.status = InboundDecision.STATUS_DISMISSED
    decision.save(update_fields=["status"])

    return {"decision_id": decision.id}
PY

cat > apps/emailing/views.py << 'PY'
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.emailing.models import InboundEmail, OutboundEmail
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
        elif not email.ai_decisions.filter(status=InboundEmail.ai_decisions.rel.related_model.STATUS_SUGGESTED).exists():
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
        latest_non_suggested_decision = None

        for decision in email.ai_decisions.all():
            if decision.status == "suggested":
                suggested_decision = decision
                break

        if not suggested_decision:
            latest_non_suggested_decision = email.ai_decisions.first()

        email.suggested_decision = suggested_decision
        email.latest_decision = suggested_decision or latest_non_suggested_decision

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


@require_POST
def apply_decision(request, pk):
    email = get_object_or_404(InboundEmail, pk=pk)
    decision = email.ai_decisions.filter(status="suggested").first()

    if decision:
        apply_inbound_decision(decision)

    return redirect(request.META.get("HTTP_REFERER", "/inbox/"))


@require_POST
def dismiss_decision(request, pk):
    email = get_object_or_404(InboundEmail, pk=pk)
    decision = email.ai_decisions.filter(status="suggested").first()

    if decision:
        dismiss_inbound_decision(decision)

    return redirect(request.META.get("HTTP_REFERER", "/inbox/"))
PY

cat > apps/emailing/urls.py << 'PY'
from django.urls import path

from .views import (
    approve_email,
    apply_decision,
    back_to_draft,
    bulk_action,
    dismiss_decision,
    generate_reply_draft,
    inbox_view,
    mark_inbound_linked,
    mark_inbound_reviewed,
    outbox_view,
    send_all,
    send_email,
)

urlpatterns = [
    path("outbox/", outbox_view, name="outbox"),
    path("outbox/<int:pk>/approve/", approve_email, name="approve_email"),
    path("outbox/<int:pk>/draft/", back_to_draft, name="back_to_draft"),
    path("outbox/<int:pk>/send/", send_email, name="send_email"),
    path("outbox/send/", send_all, name="send_all_emails"),
    path("outbox/bulk-action/", bulk_action, name="bulk_outbox_action"),

    path("inbox/", inbox_view, name="inbox"),
    path("inbox/<int:pk>/reviewed/", mark_inbound_reviewed, name="mark_inbound_reviewed"),
    path("inbox/<int:pk>/linked/", mark_inbound_linked, name="mark_inbound_linked"),
    path("inbox/<int:pk>/generate-reply/", generate_reply_draft, name="generate_reply_draft"),
    path("inbox/<int:pk>/apply-decision/", apply_decision, name="apply_decision"),
    path("inbox/<int:pk>/dismiss-decision/", dismiss_decision, name="dismiss_decision"),
]
PY

cat > apps/emailing/templates/emailing/inbox.html << 'HTML'
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>Inbox · OptiGrid CRM</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 24px; background: #f6f7f9; color: #1f2937; }
    .page { max-width: 1100px; margin: 0 auto; }
    .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; gap: 12px; flex-wrap: wrap; }
    .header-actions a { text-decoration: none; color: white; padding: 10px 14px; border-radius: 10px; font-weight: bold; margin-left: 8px; display: inline-block; }
    .go-outbox { background: #2563eb; }
    .go-leads { background: #4b5563; }
    .filters { margin-bottom: 12px; }
    .filters a { margin-right: 10px; text-decoration: none; font-weight: bold; color: #2563eb; }
    .card { background: white; border: 1px solid #e5e7eb; border-radius: 14px; padding: 16px; margin-bottom: 14px; box-shadow: 0 1px 2px rgba(0,0,0,0.04); }
    .subject { font-size: 18px; font-weight: bold; margin-bottom: 8px; }
    .meta { font-size: 13px; color: #6b7280; margin-bottom: 12px; line-height: 1.5; }
    .status, .rtype, .ai-badge { display: inline-block; padding: 4px 8px; border-radius: 999px; font-size: 12px; font-weight: bold; margin-left: 8px; text-transform: uppercase; }
    .status.new { background: #fef3c7; color: #92400e; }
    .status.reviewed { background: #dbeafe; color: #1d4ed8; }
    .status.linked { background: #dcfce7; color: #166534; }
    .rtype.interested { background: #dcfce7; color: #166534; }
    .rtype.needs_info { background: #e0f2fe; color: #0369a1; }
    .rtype.not_now { background: #fef3c7; color: #92400e; }
    .rtype.not_interested { background: #fee2e2; color: #991b1b; }
    .rtype.unclear { background: #e5e7eb; color: #374151; }

    .ai-panel {
      margin: 14px 0;
      background: #f8fafc;
      border: 1px solid #dbeafe;
      border-radius: 12px;
      padding: 14px;
    }
    .ai-title {
      font-size: 14px;
      font-weight: 700;
      color: #1d4ed8;
      margin-bottom: 10px;
    }
    .ai-grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(120px, 1fr));
      gap: 10px;
      margin-bottom: 10px;
    }
    .ai-box {
      background: white;
      border: 1px solid #e5e7eb;
      border-radius: 10px;
      padding: 10px;
    }
    .ai-box-label {
      font-size: 11px;
      color: #6b7280;
      text-transform: uppercase;
      margin-bottom: 4px;
    }
    .ai-box-value {
      font-size: 14px;
      font-weight: bold;
      color: #111827;
    }
    .ai-rationale {
      background: white;
      border: 1px solid #e5e7eb;
      border-radius: 10px;
      padding: 10px;
      font-size: 14px;
      line-height: 1.45;
      margin-bottom: 10px;
    }
    .ai-signals {
      font-size: 13px;
      color: #4b5563;
      margin-bottom: 6px;
    }
    .ai-summary {
      background: #eff6ff;
      border: 1px solid #bfdbfe;
      border-radius: 10px;
      padding: 10px;
      font-size: 14px;
      line-height: 1.45;
    }

    pre { white-space: pre-wrap; background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 10px; padding: 12px; font-family: Arial, sans-serif; font-size: 14px; line-height: 1.5; }
    .actions { margin-top: 12px; }
    .actions a { display: inline-block; text-decoration: none; padding: 8px 12px; border-radius: 8px; font-size: 14px; font-weight: bold; margin-right: 8px; margin-bottom: 8px; color: white; }
    .reviewed { background: #2563eb; }
    .linked { background: #16a34a; }
    .reply { background: #7c3aed; }
    .decision-form { display: inline-block; margin-right: 8px; margin-top: 10px; }
    .decision-btn {
      color: white;
      padding: 8px 12px;
      border: none;
      border-radius: 8px;
      font-size: 14px;
      font-weight: bold;
      cursor: pointer;
    }
    .decision-apply { background: #16a34a; }
    .decision-dismiss { background: #6b7280; }
    .empty { background: white; border: 1px dashed #d1d5db; border-radius: 14px; padding: 24px; text-align: center; color: #6b7280; }

    @media (max-width: 800px) {
      .ai-grid {
        grid-template-columns: 1fr 1fr;
      }
    }

    @media (max-width: 520px) {
      .ai-grid {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <div class="page">
    <div class="header">
      <h1>Inbox</h1>
      <div class="header-actions">
        <a class="go-leads" href="/leads/">Lead Inbox</a>
        <a class="go-outbox" href="/outbox/">Outbox</a>
      </div>
    </div>

    <div class="filters">
      <strong>By status:</strong>
      <a href="/inbox/?status=all&reply_type={{ reply_type }}">All ({{ counts.all }})</a>
      <a href="/inbox/?status=new&reply_type={{ reply_type }}">New ({{ counts.new }})</a>
      <a href="/inbox/?status=reviewed&reply_type={{ reply_type }}">Reviewed ({{ counts.reviewed }})</a>
      <a href="/inbox/?status=linked&reply_type={{ reply_type }}">Linked ({{ counts.linked }})</a>
    </div>

    <div class="filters">
      <strong>By reply type:</strong>
      <a href="/inbox/?status={{ status }}&reply_type=all">All</a>
      <a href="/inbox/?status={{ status }}&reply_type=interested">Interested ({{ counts.interested }})</a>
      <a href="/inbox/?status={{ status }}&reply_type=needs_info">Needs info ({{ counts.needs_info }})</a>
      <a href="/inbox/?status={{ status }}&reply_type=not_now">Not now ({{ counts.not_now }})</a>
      <a href="/inbox/?status={{ status }}&reply_type=not_interested">Not interested ({{ counts.not_interested }})</a>
      <a href="/inbox/?status={{ status }}&reply_type=unclear">Unclear ({{ counts.unclear }})</a>
    </div>

    {% if emails %}
      {% for e in emails %}
        <div class="card">
          <div class="subject">
            {{ e.subject }}
            <span class="status {{ e.status }}">{{ e.status }}</span>
            <span class="rtype {{ e.reply_type }}">{{ e.reply_type }}</span>
          </div>

          <div class="meta">
            Opportunity:
            {% if e.opportunity %}
              #{{ e.opportunity.id }} · {{ e.opportunity.title }}
            {% else %}
              —
            {% endif %}
            <br>
            Company:
            {% if e.opportunity %}
              {{ e.opportunity.company_name|default:"—" }}
            {% else %}
              —
            {% endif %}
            <br>
            From: {{ e.from_email|default:"(sin remitente)" }}
            <br>
            Received: {{ e.received_at }}
            {% if e.source_outbound %}
              <br>
              Source outbound: #{{ e.source_outbound.id }} · {{ e.source_outbound.subject }}
            {% endif %}
          </div>

          {% if e.ai_interpretation %}
            <div class="ai-panel">
              <div class="ai-title">AI Interpretation</div>

              <div class="ai-grid">
                <div class="ai-box">
                  <div class="ai-box-label">Intent</div>
                  <div class="ai-box-value">{{ e.ai_interpretation.intent }}</div>
                </div>
                <div class="ai-box">
                  <div class="ai-box-label">Urgency</div>
                  <div class="ai-box-value">{{ e.ai_interpretation.urgency }}</div>
                </div>
                <div class="ai-box">
                  <div class="ai-box-label">Sentiment</div>
                  <div class="ai-box-value">{{ e.ai_interpretation.sentiment }}</div>
                </div>
                <div class="ai-box">
                  <div class="ai-box-label">Confidence</div>
                  <div class="ai-box-value">{{ e.ai_interpretation.confidence }}</div>
                </div>
              </div>

              <div class="ai-rationale">
                <strong>Recommended action:</strong>
                {{ e.ai_interpretation.recommended_action }}
                <br><br>
                <strong>Rationale:</strong>
                {{ e.ai_interpretation.rationale|default:"—" }}
              </div>

              {% if e.ai_interpretation.signals_json %}
                <div class="ai-signals">
                  <strong>Signals:</strong> {{ e.ai_interpretation.signals_json }}
                </div>
              {% endif %}

              {% if e.latest_decision %}
                <div class="ai-summary">
                  <strong>Suggested decision:</strong>
                  {{ e.latest_decision.summary|default:e.latest_decision.action_type }}
                  <br>
                  <strong>Approval required:</strong>
                  {% if e.latest_decision.requires_approval %}yes{% else %}no{% endif %}
                  <br>
                  <strong>Status:</strong> {{ e.latest_decision.status }}

                  {% if e.suggested_decision %}
                    <div>
                      <form method="post" action="/inbox/{{ e.id }}/apply-decision/" class="decision-form">
                        {% csrf_token %}
                        <button type="submit" class="decision-btn decision-apply">Apply Decision</button>
                      </form>

                      <form method="post" action="/inbox/{{ e.id }}/dismiss-decision/" class="decision-form">
                        {% csrf_token %}
                        <button type="submit" class="decision-btn decision-dismiss">Dismiss</button>
                      </form>
                    </div>
                  {% endif %}
                </div>
              {% endif %}
            </div>
          {% endif %}

          <pre>{{ e.body }}</pre>

          <div class="actions">
            <a class="reply" href="/inbox/{{ e.id }}/generate-reply/">Generate reply draft</a>

            {% if e.status == "new" %}
              <a class="reviewed" href="/inbox/{{ e.id }}/reviewed/">Mark reviewed</a>
              <a class="linked" href="/inbox/{{ e.id }}/linked/">Mark linked</a>
            {% elif e.status == "reviewed" %}
              <a class="linked" href="/inbox/{{ e.id }}/linked/">Mark linked</a>
            {% endif %}
          </div>
        </div>
      {% endfor %}
    {% else %}
      <div class="empty">
        No hay replies todavía.
      </div>
    {% endif %}
  </div>
</body>
</html>
HTML

cat > apps/emailing/tests.py << 'PY'
from django.test import TestCase
from django.utils import timezone

from apps.emailing.models import (
    InboundDecision,
    InboundEmail,
    InboundInterpretation,
    OutboundEmail,
)
from apps.emailing.services.inbound_decision_apply_service import (
    apply_inbound_decision,
    dismiss_inbound_decision,
)
from apps.emailing.services.inbound_decision_engine import build_inbound_decision
from apps.emailing.services.inbound_interpreter import interpret_inbound_email
from apps.opportunities.models import Opportunity
from apps.tasks.models import CRMTask


class DummyOpportunity:
    id = 123


class DummyInbound:
    def __init__(self, reply_type, body="", opportunity=None):
        self.reply_type = reply_type
        self.body = body
        self.opportunity = opportunity


class InboundAnalysisServiceUnitTest(TestCase):
    def test_interested_maps_to_advance_opportunity(self):
        inbound = DummyInbound(
            reply_type="interested",
            body="We are interested. Let's talk this week.",
            opportunity=DummyOpportunity(),
        )

        interpretation = interpret_inbound_email(inbound)
        decision = build_inbound_decision(inbound, interpretation)

        self.assertEqual(interpretation.intent, "interested")
        self.assertEqual(interpretation.recommended_action, "advance_opportunity")
        self.assertEqual(interpretation.sentiment, "positive")
        self.assertEqual(interpretation.urgency, "high")
        self.assertEqual(decision.action_type, "advance_opportunity")
        self.assertTrue(decision.requires_approval)

    def test_not_now_maps_to_followup(self):
        inbound = DummyInbound(
            reply_type="not_now",
            body="Not now, maybe later.",
            opportunity=DummyOpportunity(),
        )

        interpretation = interpret_inbound_email(inbound)
        decision = build_inbound_decision(inbound, interpretation)

        self.assertEqual(interpretation.intent, "delay")
        self.assertEqual(interpretation.recommended_action, "schedule_followup")
        self.assertEqual(interpretation.sentiment, "neutral")
        self.assertEqual(interpretation.urgency, "low")
        self.assertEqual(decision.action_type, "schedule_followup")
        self.assertFalse(decision.requires_approval)

    def test_not_interested_maps_to_mark_lost(self):
        inbound = DummyInbound(
            reply_type="not_interested",
            body="No thanks, not interested.",
            opportunity=DummyOpportunity(),
        )

        interpretation = interpret_inbound_email(inbound)
        decision = build_inbound_decision(inbound, interpretation)

        self.assertEqual(interpretation.intent, "rejection")
        self.assertEqual(interpretation.recommended_action, "mark_lost")
        self.assertEqual(interpretation.sentiment, "negative")
        self.assertEqual(interpretation.urgency, "low")
        self.assertEqual(decision.action_type, "mark_lost")
        self.assertTrue(decision.requires_approval)


class ApplyInboundDecisionServiceTest(TestCase):
    def setUp(self):
        self.opportunity = Opportunity.objects.create(
            title="Test Opportunity",
            company_name="ACME",
            stage="new",
        )

        self.inbound = InboundEmail.objects.create(
            opportunity=self.opportunity,
            from_email="lead@example.com",
            subject="Interested in learning more",
            body="Please send more information.",
            status=InboundEmail.STATUS_NEW,
            reply_type=InboundEmail.REPLY_NEEDS_INFO,
            received_at=timezone.now(),
        )

        self.interpretation = InboundInterpretation.objects.create(
            inbound_email=self.inbound,
            intent=InboundInterpretation.INTENT_OBJECTION,
            urgency=InboundInterpretation.URGENCY_MEDIUM,
            sentiment=InboundInterpretation.SENTIMENT_NEUTRAL,
            recommended_action=InboundInterpretation.ACTION_SEND_INFORMATION,
            confidence=0.85,
            rationale="Needs more information",
            signals_json={"needs_info": True},
        )

    def test_apply_schedule_followup_creates_task(self):
        decision = InboundDecision.objects.create(
            inbound_email=self.inbound,
            interpretation=self.interpretation,
            action_type=InboundDecision.ACTION_SCHEDULE_FOLLOWUP,
            status=InboundDecision.STATUS_SUGGESTED,
            summary="Schedule a follow-up in a few days",
            payload_json={},
            requires_approval=False,
        )

        result = apply_inbound_decision(decision)

        decision.refresh_from_db()

        self.assertEqual(decision.status, InboundDecision.STATUS_APPLIED)
        self.assertIsNotNone(decision.applied_at)
        self.assertEqual(CRMTask.objects.count(), 1)
        self.assertIsNotNone(result["task_id"])

    def test_apply_send_information_creates_draft(self):
        decision = InboundDecision.objects.create(
            inbound_email=self.inbound,
            interpretation=self.interpretation,
            action_type=InboundDecision.ACTION_SEND_INFORMATION,
            status=InboundDecision.STATUS_SUGGESTED,
            summary="Send company overview and next steps",
            payload_json={},
            requires_approval=True,
        )

        result = apply_inbound_decision(decision)

        decision.refresh_from_db()
        outbound = OutboundEmail.objects.get(id=result["outbound_id"])

        self.assertEqual(decision.status, InboundDecision.STATUS_APPLIED)
        self.assertEqual(outbound.status, OutboundEmail.STATUS_DRAFT)
        self.assertEqual(outbound.email_type, OutboundEmail.TYPE_FOLLOWUP)
        self.assertEqual(outbound.to_email, "lead@example.com")
        self.assertEqual(outbound.source_inbound_id, self.inbound.id)

    def test_apply_advance_opportunity_moves_stage(self):
        decision = InboundDecision.objects.create(
            inbound_email=self.inbound,
            interpretation=self.interpretation,
            action_type=InboundDecision.ACTION_ADVANCE_OPPORTUNITY,
            status=InboundDecision.STATUS_SUGGESTED,
            summary="Advance opportunity to next stage",
            payload_json={},
            requires_approval=True,
        )

        result = apply_inbound_decision(decision)

        self.opportunity.refresh_from_db()
        decision.refresh_from_db()

        self.assertEqual(decision.status, InboundDecision.STATUS_APPLIED)
        self.assertEqual(self.opportunity.stage, "qualified")
        self.assertEqual(result["opportunity_stage"], "qualified")

    def test_apply_mark_lost(self):
        decision = InboundDecision.objects.create(
            inbound_email=self.inbound,
            interpretation=self.interpretation,
            action_type=InboundDecision.ACTION_MARK_LOST,
            status=InboundDecision.STATUS_SUGGESTED,
            summary="Mark opportunity as lost",
            payload_json={},
            requires_approval=True,
        )

        apply_inbound_decision(decision)

        self.opportunity.refresh_from_db()
        decision.refresh_from_db()

        self.assertEqual(decision.status, InboundDecision.STATUS_APPLIED)
        self.assertEqual(self.opportunity.stage, "lost")

    def test_dismiss_decision(self):
        decision = InboundDecision.objects.create(
            inbound_email=self.inbound,
            interpretation=self.interpretation,
            action_type=InboundDecision.ACTION_SEND_CLARIFICATION,
            status=InboundDecision.STATUS_SUGGESTED,
            summary="Ask for clarification",
            payload_json={},
            requires_approval=True,
        )

        dismiss_inbound_decision(decision)
        decision.refresh_from_db()

        self.assertEqual(decision.status, InboundDecision.STATUS_DISMISSED)
PY

chmod +x refactor_inbox_intelligence_v2.sh

echo
echo "Script generado:"
echo "  $PROJECT_ROOT/refactor_inbox_intelligence_v2.sh"
echo
echo "Ejecuta:"
echo "  ./refactor_inbox_intelligence_v2.sh"
echo
echo "Después prueba:"
echo "  python manage.py test apps.emailing"
