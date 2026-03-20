# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/lead_research/services/lead_promotion.py
from django.db import transaction

from apps.opportunities.models import Opportunity
from apps.recommendations.models import AIRecommendation
from apps.tasks.models import CRMTask
from apps.emailing.models import OutboundEmail


def promote_lead_to_opportunity(lead):
    with transaction.atomic():
        title = f"Outbound - {lead.company_name}"

        opportunity = Opportunity.objects.filter(
            title=title,
            company_name=lead.company_name,
            stage="new",
        ).order_by("-id").first()

        if not opportunity:
            opportunity = Opportunity.objects.create(
                title=title,
                company_name=lead.company_name,
                stage="new",
                confidence=lead.confidence,
                summary="Lead detected via signals",
            )

        recommendation = AIRecommendation.objects.filter(
            scope_type="opportunity",
            scope_id=opportunity.id,
            recommendation_type="contact_strategy",
        ).order_by("-id").first()

        if not recommendation:
            recommendation = AIRecommendation.objects.create(
                scope_type="opportunity",
                scope_id=opportunity.id,
                recommendation_type="contact_strategy",
                recommendation_text=f"Initiate contact with {lead.company_name} based on detected signals",
                confidence=lead.confidence,
                status="new",
            )

        task = CRMTask.objects.filter(
            opportunity=opportunity,
            task_type="define_next_action",
            title=f"Prepare outreach to {lead.company_name}",
        ).order_by("-id").first()

        if not task:
            task = CRMTask.objects.create(
                opportunity=opportunity,
                task_type="define_next_action",
                title=f"Prepare outreach to {lead.company_name}",
                status="pending",
                source="lead_research",
            )

        outbound = OutboundEmail.objects.filter(opportunity=opportunity).order_by("-id").first()

        if not outbound:
            subject = f"Infrastructure support for {lead.company_name}"
            body = f'''Hi,

I noticed that {lead.company_name} might be experiencing growth in infrastructure or operations.

I help companies improve reliability, scalability and operational efficiency in their IT environments.

Would it make sense to have a quick conversation?

Best regards,
Hans'''.strip()

            outbound = OutboundEmail.objects.create(
                opportunity=opportunity,
                email_type=OutboundEmail.TYPE_FIRST_CONTACT,
                to_email="",
                subject=subject,
                body=body,
                status=OutboundEmail.STATUS_DRAFT,
                generated_by="ai",
            )

        if hasattr(opportunity, "source_task") and not opportunity.source_task_id:
            opportunity.source_task = task

        if hasattr(opportunity, "source_recommendation") and not opportunity.source_recommendation_id:
            opportunity.source_recommendation = recommendation

        opportunity.save()

        return {
            "opportunity_id": opportunity.id,
            "recommendation_id": recommendation.id,
            "task_id": task.id,
            "outbound_email_id": outbound.id,
        }
