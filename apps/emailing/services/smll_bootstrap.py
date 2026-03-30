from decimal import Decimal

from django.utils import timezone

from apps.emailing.models import InboundEmail
from apps.opportunities.models import Opportunity
from apps.simulated_personas.models import SimulatedPersona
from apps.tenancy.models import MailboxAccount, OperatingOrganization


def get_or_create_default_org():
    org = OperatingOrganization.objects.filter(slug="optigrid-simulation-lab").first()
    if org is not None:
        return org

    return OperatingOrganization.objects.create(
        name="OptiGrid Simulation Lab",
        slug="optigrid-simulation-lab",
        is_simulated=True,
        status=OperatingOrganization.Status.ACTIVE,
    )


def get_default_mailbox():
    org = get_or_create_default_org()

    mailbox = MailboxAccount.objects.filter(
        operating_organization=org,
        account_key="runtime-simulation-mailbox",
    ).first()

    if mailbox is not None:
        return mailbox

    return MailboxAccount.objects.create(
        operating_organization=org,
        display_name="Runtime Mailbox",
        email="runtime@simulation.local",
        account_key="runtime-simulation-mailbox",
        provider="mail_embedded",
        is_primary=True,
        status=MailboxAccount.Status.ACTIVE,
        metadata={},
    )


def ensure_generic_persona(mailbox_account):
    org = mailbox_account.operating_organization

    persona = SimulatedPersona.objects.filter(
        operating_organization=org,
        mailbox_account=mailbox_account,
        slug="generic-buyer",
        is_active=True,
    ).first()

    if persona is not None:
        return persona

    return SimulatedPersona.objects.create(
        operating_organization=org,
        mailbox_account=mailbox_account,
        slug="generic-buyer",
        full_name="Generic Buyer",
        first_name="Generic",
        last_name="Buyer",
        job_title="Operations Manager",
        simulated_company_name="Generic Manufacturing GmbH",
        seniority=SimulatedPersona.Seniority.MID,
        notes="Bootstrap persona for SMLL integration tests.",
        character_seed="Pragmatic B2B buyer.",
        formality=Decimal("0.50"),
        patience=Decimal("0.50"),
        risk_tolerance=Decimal("0.50"),
        change_openness=Decimal("0.50"),
        cooperation=Decimal("0.60"),
        resistance=Decimal("0.40"),
        responsiveness=Decimal("0.60"),
        detail_orientation=Decimal("0.50"),
        communication_style=SimulatedPersona.CommunicationStyle.BALANCED,
        preferred_language="en",
        typical_reply_latency_hours=24,
        goals=["Improve operational reliability."],
        pains=["Fragmented systems and manual work."],
        priorities=["Low-risk improvements with clear ROI."],
        internal_pressures=[],
        budget_context="Budget-sensitive but open to justified improvements.",
        decision_frame=SimulatedPersona.DecisionFrame.MANAGER_REVIEW,
        decision_criteria=["practical value", "clarity", "low risk"],
        blockers=[],
        interest_level=Decimal("0.50"),
        trust_level=Decimal("0.50"),
        saturation_level=Decimal("0.20"),
        urgency_level=Decimal("0.30"),
        frustration_level=Decimal("0.20"),
        relational_temperature=SimulatedPersona.Temperature.NEUTRAL,
        is_active=True,
    )


def create_opportunity(from_email):
    domain = from_email.split("@")[-1] if "@" in from_email else ""
    return Opportunity.objects.create(
        title=f"Lead from {from_email}",
        company_name=domain,
        summary="Simulated inbound lead via SMLL",
    )


def create_simulated_inbound_email(
    subject,
    body,
    from_email,
    *,
    mailbox_account=None,
    source_outbound=None,
):
    opportunity = create_opportunity(from_email)

    return InboundEmail.objects.create(
        opportunity=opportunity,
        source_outbound=source_outbound,
        from_email=from_email,
        subject=subject,
        body=body,
        received_at=timezone.now(),
    )
