from decimal import Decimal

from django.db import models
from django.test import TestCase

from apps.simulated_personas.models import SimulatedPersona
from apps.simulated_personas.runtime.smll_engine import (
    SimulatedIncomingMessage,
    build_simulated_reply,
)
from apps.tenancy.models import MailboxAccount, OperatingOrganization


class SMLLEngineV0Tests(TestCase):
    def setUp(self):
        self.org = self._get_or_create_org()
        self.mailbox = self._get_or_create_mailbox()
        self.persona = SimulatedPersona.objects.create(
            operating_organization=self.org,
            mailbox_account=self.mailbox,
            slug="marta-vogel-runtime",
            full_name="Marta Vogel",
            first_name="Marta",
            job_title="Head of Operations",
            simulated_company_name="Nordstern Systems",
            seniority=SimulatedPersona.Seniority.DIRECTOR,
            formality=Decimal("0.80"),
            communication_style=SimulatedPersona.CommunicationStyle.DIRECT,
            priorities=["Operational reliability"],
            pains=["Too much vendor noise"],
            decision_frame=SimulatedPersona.DecisionFrame.MANAGER_REVIEW,
        )

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
            kwargs["description"] = "Tenant de pruebas para smll engine."

        return OperatingOrganization.objects.create(**kwargs)

    def _get_or_create_mailbox(self):
        field_names = {f.name for f in MailboxAccount._meta.concrete_fields}

        lookup_field = None
        lookup_value = None

        if "email" in field_names:
            lookup_field = "email"
            lookup_value = "runtime@simulation.local"
        elif "email_address" in field_names:
            lookup_field = "email_address"
            lookup_value = "runtime@simulation.local"
        elif "account_key" in field_names:
            lookup_field = "account_key"
            lookup_value = "runtime-simulation-mailbox"

        existing = None
        if lookup_field is not None:
            existing = MailboxAccount.objects.filter(**{lookup_field: lookup_value}).first()

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

            if name == "email":
                kwargs[name] = "runtime@simulation.local"
            elif name == "email_address":
                kwargs[name] = "runtime@simulation.local"
            elif name == "display_name":
                kwargs[name] = "Runtime Mailbox"
            elif name == "name":
                kwargs[name] = "Runtime Mailbox"
            elif name == "account_key":
                kwargs[name] = "runtime-simulation-mailbox"
            elif name == "slug":
                kwargs[name] = "runtime-simulation-mailbox"
            elif name == "provider_key":
                kwargs[name] = "mail_embedded"
            elif name == "provider":
                kwargs[name] = "mail_embedded"
            elif name == "mailbox_type":
                kwargs[name] = "shared"
            elif name == "status":
                kwargs[name] = "active"
            elif name == "metadata":
                kwargs[name] = {}
            elif isinstance(field, models.BooleanField):
                kwargs[name] = True
            elif isinstance(field, models.CharField):
                kwargs[name] = f"test_{name}"
            elif isinstance(field, models.TextField):
                kwargs[name] = f"test_{name}"
            elif isinstance(field, models.IntegerField):
                kwargs[name] = 0

        return MailboxAccount.objects.create(**kwargs)

    def test_smll_engine_generates_reply(self):
        result = build_simulated_reply(
            operating_organization=self.org,
            incoming_message=SimulatedIncomingMessage(
                subject="Quick discussion",
                body="We are interested. Could we schedule a short call next week?",
                sender_name="Hans",
            ),
            persona_slug=self.persona.slug,
        )

        reply_lower = result.reply_body.lower()

        self.assertEqual(result.persona_id, self.persona.id)
        self.assertTrue(result.reply_body.startswith("Hello Hans,"))
        self.assertIn("meeting_request", result.detected_signals)
        self.assertTrue(
            ("short" in reply_lower and "discussion" in reply_lower)
            or ("short" in reply_lower and "call" in reply_lower)
        )

    def test_smll_engine_updates_state(self):
        before_interest = self.persona.interest_level

        result = build_simulated_reply(
            operating_organization=self.org,
            incoming_message=SimulatedIncomingMessage(
                subject="Potential fit",
                body="This could be relevant for us and I would like to understand the scope.",
                sender_name="Hans",
            ),
            persona_slug=self.persona.slug,
        )

        self.persona.refresh_from_db()
        self.assertGreater(self.persona.interest_level, before_interest)
        self.assertEqual(
            result.state_after["relational_temperature"],
            SimulatedPersona.Temperature.WARM,
        )

    def test_smll_engine_requires_mailbox_resolution(self):
        self.persona.mailbox_account = None
        self.persona.save(update_fields=["mailbox_account"])

        with self.assertRaises(ValueError):
            build_simulated_reply(
                operating_organization=self.org,
                incoming_message=SimulatedIncomingMessage(
                    subject="Hello",
                    body="Just checking relevance.",
                ),
                persona_slug=self.persona.slug,
            )

    def test_smll_engine_persists_memory(self):
        result = build_simulated_reply(
            operating_organization=self.org,
            incoming_message=SimulatedIncomingMessage(
                subject="Budget concerns",
                body="The idea is interesting, but budget is limited and we need a clear case.",
                sender_name="Hans",
            ),
            persona_slug=self.persona.slug,
        )

        self.assertTrue(
            self.persona.memories.filter(title="Interaction: Budget concerns").exists()
        )
        self.assertIn("budget_pressure", result.detected_signals)
