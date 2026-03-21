# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/emailing/services/reply_generator.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
from apps.emailing.models import InboundEmail, OutboundEmail


def _build_followup_subject(inbound: InboundEmail) -> str:
    if inbound.subject.lower().startswith("re:"):
        return inbound.subject
    return f"Re: {inbound.subject}"


def _build_followup_body(inbound: InboundEmail) -> str:
    company = inbound.opportunity.company_name or "your team"

    if inbound.reply_type == InboundEmail.REPLY_INTERESTED:
        return f"""Hi,

Thanks for your reply.

Absolutely — I’d be happy to share more detail on how I could support {company}, especially around infrastructure reliability, scalability, and operational efficiency.

A practical next step could be a short call to understand your current setup and priorities, and from there I can suggest the most relevant approach.

Would sometime next week work for a brief conversation?

Best regards,
Hans""".strip()

    if inbound.reply_type == InboundEmail.REPLY_NEEDS_INFO:
        return f"""Hi,

Thanks for coming back to me.

In practical terms, I help companies like {company} with areas such as infrastructure stability, operational improvements, scalability, and support for growing internal IT environments.

That can include reviewing current bottlenecks, improving reliability, and helping define a more robust operating setup without adding unnecessary complexity.

If useful, I can send a short summary tailored to your situation or we can have a quick intro call.

Best regards,
Hans""".strip()

    if inbound.reply_type == InboundEmail.REPLY_NOT_NOW:
        return f"""Hi,

Thanks for the quick reply.

Understood — that makes sense. I’ll leave it here for now.

If priorities change later on and {company} needs support around infrastructure, scalability, or operational improvements, feel free to reach out and I’d be happy to continue the conversation.

Best regards,
Hans""".strip()

    if inbound.reply_type == InboundEmail.REPLY_NOT_INTERESTED:
        return """Hi,

Thanks for letting me know.

Understood, and I appreciate the reply. I won’t insist further.

Wishing you and your team all the best.

Best regards,
Hans""".strip()

    return f"""Hi,

Thanks for your reply.

Happy to clarify. My message was based on the idea that {company} may be dealing with infrastructure or operational growth challenges, and my work is focused on helping teams improve reliability, scalability, and overall technical operations.

If useful, I can explain it more concretely in one short paragraph based on your context.

Best regards,
Hans""".strip()


def generate_followup_draft_from_inbound(inbound: InboundEmail) -> OutboundEmail:
    existing = OutboundEmail.objects.filter(
        source_inbound=inbound,
        email_type=OutboundEmail.TYPE_FOLLOWUP,
    ).first()

    if existing:
        return existing

    outbound = OutboundEmail.objects.create(
        opportunity=inbound.opportunity,
        source_inbound=inbound,
        email_type=OutboundEmail.TYPE_FOLLOWUP,
        to_email=inbound.from_email,
        subject=_build_followup_subject(inbound),
        body=_build_followup_body(inbound),
        status=OutboundEmail.STATUS_DRAFT,
        generated_by="ai",
    )
    return outbound
