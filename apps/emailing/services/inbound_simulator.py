# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/emailing/services/inbound_simulator.py
from django.utils import timezone

from apps.emailing.models import InboundEmail, OutboundEmail


def _build_reply_payload(outbound: OutboundEmail) -> dict:
    company = outbound.opportunity.company_name or "your company"
    email_id = outbound.id or 0

    patterns = [
        {
            "reply_type": InboundEmail.REPLY_INTERESTED,
            "subject": f"Re: {outbound.subject}",
            "body": (
                f"Hi Hans,\n\n"
                f"This looks interesting for {company}. Could you share a bit more detail about your approach and next steps?\n\n"
                f"Best regards"
            ),
        },
        {
            "reply_type": InboundEmail.REPLY_NEEDS_INFO,
            "subject": f"Re: {outbound.subject}",
            "body": (
                f"Hello,\n\n"
                f"Can you clarify what kind of infrastructure support you provide and whether you work with mid-sized teams like ours?\n\n"
                f"Thanks"
            ),
        },
        {
            "reply_type": InboundEmail.REPLY_NOT_NOW,
            "subject": f"Re: {outbound.subject}",
            "body": (
                f"Hi,\n\n"
                f"Thanks for reaching out. This is not a priority right now, but feel free to check again later this quarter.\n\n"
                f"Regards"
            ),
        },
        {
            "reply_type": InboundEmail.REPLY_NOT_INTERESTED,
            "subject": f"Re: {outbound.subject}",
            "body": (
                f"Hello,\n\n"
                f"Thank you for the message. We are not looking for external support in this area at the moment.\n\n"
                f"Best"
            ),
        },
        {
            "reply_type": InboundEmail.REPLY_UNCLEAR,
            "subject": f"Re: {outbound.subject}",
            "body": (
                f"Hi,\n\n"
                f"Could you explain a bit more specifically what problem you think we may have?\n\n"
                f"Thanks"
            ),
        },
    ]

    idx = email_id % len(patterns)
    return patterns[idx]


def simulate_inbound_reply_for_outbound(outbound: OutboundEmail) -> InboundEmail:
    existing = InboundEmail.objects.filter(source_outbound=outbound).first()
    if existing:
        return existing

    payload = _build_reply_payload(outbound)

    inbound = InboundEmail.objects.create(
        opportunity=outbound.opportunity,
        source_outbound=outbound,
        from_email=f"contact@{(outbound.opportunity.company_name or 'company').lower().replace(' ', '').replace('.', '')}.com",
        subject=payload["subject"],
        body=payload["body"],
        status=InboundEmail.STATUS_NEW,
        reply_type=payload["reply_type"],
        received_at=timezone.now(),
    )
    return inbound
