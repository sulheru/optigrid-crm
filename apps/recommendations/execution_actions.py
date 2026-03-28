from __future__ import annotations

from apps.emailing.models import InboundDecision, InboundEmail, OutboundEmail
from apps.opportunities.models import Opportunity
from apps.recommendations.models import AIRecommendation
from apps.tasks.services.materialize import materialize_recommendation_as_task


class RecommendationExecutionError(Exception):
    pass


def normalized(value) -> str:
    return (value or "").strip().lower()


def resolve_inbound_for_recommendation(recommendation: AIRecommendation) -> InboundEmail | None:
    scope_type = normalized(getattr(recommendation, "scope_type", ""))
    scope_id = getattr(recommendation, "scope_id", None)

    if scope_type == "inbound_email" and scope_id not in (None, ""):
        return InboundEmail.objects.filter(pk=scope_id).first()

    if scope_type == "inbound_decision" and scope_id not in (None, ""):
        decision = (
            InboundDecision.objects.filter(pk=scope_id)
            .select_related("inbound_email")
            .first()
        )
        if decision is not None:
            return decision.inbound_email

    if scope_type == "opportunity" and scope_id not in (None, ""):
        return (
            InboundEmail.objects.filter(opportunity_id=scope_id)
            .order_by("-received_at", "-created_at", "-id")
            .first()
        )

    return None


def resolve_opportunity_for_recommendation(recommendation: AIRecommendation) -> Opportunity | None:
    scope_type = normalized(getattr(recommendation, "scope_type", ""))
    scope_id = getattr(recommendation, "scope_id", None)

    if scope_type == "opportunity" and scope_id not in (None, ""):
        return Opportunity.objects.filter(pk=scope_id).first()

    if scope_type == "inbound_decision" and scope_id not in (None, ""):
        decision = (
            InboundDecision.objects.filter(pk=scope_id)
            .select_related("inbound_email__opportunity")
            .first()
        )
        if decision is not None and decision.inbound_email_id:
            return decision.inbound_email.opportunity

    inbound = resolve_inbound_for_recommendation(recommendation)
    if inbound and inbound.opportunity_id:
        return inbound.opportunity

    return None


def reply_subject_from_inbound(inbound: InboundEmail) -> str:
    subject = (getattr(inbound, "subject", "") or "").strip()
    if not subject:
        return "Re:"
    if subject.lower().startswith("re:"):
        return subject
    return f"Re: {subject}"


def reply_body_from_recommendation(recommendation: AIRecommendation) -> str:
    summary = (getattr(recommendation, "recommendation_text", "") or "").strip()
    if not summary:
        summary = "Gracias por tu mensaje. Quedo atento para avanzar."

    return (
        "Hola,\n\n"
        "Gracias por tu mensaje.\n\n"
        f"{summary}\n\n"
        "Quedo atento.\n"
    )


def create_reply_draft_from_recommendation(
    recommendation: AIRecommendation,
) -> OutboundEmail:
    existing = OutboundEmail.objects.filter(source_recommendation=recommendation).first()
    if existing:
        return existing

    inbound = resolve_inbound_for_recommendation(recommendation)
    opportunity = resolve_opportunity_for_recommendation(recommendation)

    if inbound is None:
        raise RecommendationExecutionError(
            "No se puede generar draft: la recomendación no tiene inbound asociado."
        )

    return OutboundEmail.objects.create(
        opportunity=opportunity,
        source_inbound=inbound,
        source_recommendation=recommendation,
        email_type=OutboundEmail.TYPE_FOLLOWUP,
        to_email=inbound.from_email,
        subject=reply_subject_from_inbound(inbound),
        body=reply_body_from_recommendation(recommendation),
        status=OutboundEmail.STATUS_DRAFT,
        generated_by="ai",
    )


def advance_opportunity(opportunity: Opportunity | None) -> str | None:
    if not opportunity:
        raise RecommendationExecutionError("No se puede avanzar: no hay opportunity asociada.")

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


def mark_opportunity_lost(opportunity: Opportunity | None) -> str:
    if not opportunity:
        raise RecommendationExecutionError("No se puede marcar perdida: no hay opportunity asociada.")

    opportunity.stage = "lost"
    opportunity.save(update_fields=["stage", "updated_at"])
    return "lost"


def materialize_task_from_recommendation(recommendation: AIRecommendation):
    return materialize_recommendation_as_task(recommendation)
