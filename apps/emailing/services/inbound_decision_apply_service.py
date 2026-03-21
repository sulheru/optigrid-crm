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
