from decimal import Decimal

from django.db import models
from django.test import TestCase

from apps.simulated_personas.models import SimulatedPersona, SimulatedPersonaMemory
from apps.simulated_personas.services.prompt_builder import (
    build_simulated_persona_prompt_context,
    build_simulated_persona_system_prompt,
)
from apps.tenancy.models import MailboxAccount, OperatingOrganization


class SimulatedPersonaModelTests(TestCase):
    def setUp(self):
        self.org = self._get_or_create_org()
        self.mailbox = self._get_or_create_mailbox()

    def _get_or_create_org(self):
        existing = OperatingOrganization.objects.filter(slug="optigrid-simulation-lab").first()
        if existing:
            return existing

        kwargs = {}
        field_names = {f.name for f in OperatingOrganization._meta.concrete_fields}

        if "name" in field_names:
            kwargs["name"] = "OptiGrid Simulation Lab"
        if "slug" in field_names:
            kwargs["slug"] = "optigrid-simulation-lab"
        if "description" in field_names:
            kwargs["description"] = "Tenant de pruebas para simulated personas."

        return OperatingOrganization.objects.create(**kwargs)

    def _get_or_create_mailbox(self):
        existing = None
        field_names = {f.name for f in MailboxAccount._meta.concrete_fields}

        if "email_address" in field_names:
            existing = MailboxAccount.objects.filter(email_address="alex@simulation.local").first()
        elif "address" in field_names:
            existing = MailboxAccount.objects.filter(address="alex@simulation.local").first()

        if existing:
            return existing

        kwargs = {}

        for field in MailboxAccount._meta.concrete_fields:
            if field.primary_key or field.auto_created:
                continue
            if field.has_default():
                continue
            if getattr(field, "null", False):
                continue

            name = field.name

            if name in ("operating_organization", "organization", "tenant", "org"):
                kwargs[name] = self.org
                continue

            if isinstance(field, models.ForeignKey):
                continue

            if name == "email_address":
                kwargs[name] = "alex@simulation.local"
            elif name == "address":
                kwargs[name] = "alex@simulation.local"
            elif name == "display_name":
                kwargs[name] = "Alex Lab"
            elif name == "name":
                kwargs[name] = "Alex Lab"
            elif name == "slug":
                kwargs[name] = "alex-simulation-mailbox"
            elif name == "provider_key":
                kwargs[name] = "mail_embedded"
            elif name == "provider":
                kwargs[name] = "mail_embedded"
            elif name == "mailbox_type":
                kwargs[name] = "shared"
            elif name == "status":
                kwargs[name] = "active"
            elif isinstance(field, models.BooleanField):
                kwargs[name] = True
            elif isinstance(field, models.CharField):
                kwargs[name] = f"test_{name}"
            elif isinstance(field, models.TextField):
                kwargs[name] = f"test_{name}"
            elif isinstance(field, models.IntegerField):
                kwargs[name] = 0

        return MailboxAccount.objects.create(**kwargs)

    def test_persona_is_scoped_to_tenant_and_mailbox(self):
        persona = SimulatedPersona.objects.create(
            operating_organization=self.org,
            mailbox_account=self.mailbox,
            slug="marta-vogel",
            full_name="Marta Vogel",
            job_title="Head of Operations",
            simulated_company_name="Nordstern Systems",
            seniority=SimulatedPersona.Seniority.DIRECTOR,
        )

        self.assertEqual(persona.operating_organization, self.org)
        self.assertEqual(persona.mailbox_account, self.mailbox)

    def test_state_delta_is_bounded(self):
        persona = SimulatedPersona.objects.create(
            operating_organization=self.org,
            slug="leo-krauss",
            full_name="Leo Krauss",
            interest_level=Decimal("0.95"),
            frustration_level=Decimal("0.05"),
        )

        persona.apply_state_delta(
            interest_delta=Decimal("0.30"),
            frustration_delta=Decimal("-0.50"),
            save=False,
        )

        self.assertEqual(persona.interest_level, Decimal("1.00"))
        self.assertEqual(persona.frustration_level, Decimal("0.00"))

    def test_prompt_builder_includes_memory(self):
        persona = SimulatedPersona.objects.create(
            operating_organization=self.org,
            mailbox_account=self.mailbox,
            slug="helen-fischer",
            full_name="Helen Fischer",
            job_title="IT Director",
            simulated_company_name="Helios Freight",
            seniority=SimulatedPersona.Seniority.DIRECTOR,
            communication_style=SimulatedPersona.CommunicationStyle.DIRECT,
            interest_level=Decimal("0.70"),
            trust_level=Decimal("0.60"),
        )
        SimulatedPersonaMemory.objects.create(
            persona=persona,
            kind=SimulatedPersonaMemory.MemoryKind.OBJECTION,
            title="Vendor fatigue",
            content="Has low tolerance for generic outreach due to vendor overload.",
            salience=Decimal("0.90"),
        )

        context = build_simulated_persona_prompt_context(persona)
        prompt = build_simulated_persona_system_prompt(persona)

        self.assertEqual(context["identity"]["full_name"], "Helen Fischer")
        self.assertEqual(len(context["memory"]), 1)
        self.assertIn("Vendor fatigue", prompt)
        self.assertIn("Helen Fischer", prompt)
