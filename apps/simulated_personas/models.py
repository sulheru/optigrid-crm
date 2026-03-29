from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


SCALE_VALIDATORS = [MinValueValidator(Decimal("0.00")), MaxValueValidator(Decimal("1.00"))]


class SimulatedPersonaQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def for_operating_organization(self, operating_organization):
        return self.filter(operating_organization=operating_organization)

    def for_mailbox_account(self, mailbox_account):
        return self.filter(mailbox_account=mailbox_account)


class SimulatedPersona(models.Model):
    class Seniority(models.TextChoices):
        INTERN = "intern", "Intern"
        JUNIOR = "junior", "Junior"
        MID = "mid", "Mid"
        SENIOR = "senior", "Senior"
        LEAD = "lead", "Lead"
        DIRECTOR = "director", "Director"
        VP = "vp", "VP"
        C_LEVEL = "c_level", "C-Level"
        OWNER = "owner", "Owner"

    class CommunicationStyle(models.TextChoices):
        CONCISE = "concise", "Concise"
        BALANCED = "balanced", "Balanced"
        EXPLANATORY = "explanatory", "Explanatory"
        RELATIONAL = "relational", "Relational"
        DIRECT = "direct", "Direct"

    class DecisionFrame(models.TextChoices):
        INDIVIDUAL = "individual", "Individual"
        MANAGER_REVIEW = "manager_review", "Manager Review"
        COMMITTEE = "committee", "Committee"
        PROCUREMENT = "procurement", "Procurement"
        EXEC_SPONSOR = "exec_sponsor", "Executive Sponsor"
        UNKNOWN = "unknown", "Unknown"

    class Temperature(models.TextChoices):
        COLD = "cold", "Cold"
        GUARDED = "guarded", "Guarded"
        NEUTRAL = "neutral", "Neutral"
        WARM = "warm", "Warm"
        ENGAGED = "engaged", "Engaged"
        FRICTION = "friction", "Friction"

    operating_organization = models.ForeignKey(
        "tenancy.OperatingOrganization",
        on_delete=models.CASCADE,
        related_name="simulated_personas",
    )
    mailbox_account = models.ForeignKey(
        "tenancy.MailboxAccount",
        on_delete=models.SET_NULL,
        related_name="simulated_personas",
        null=True,
        blank=True,
        help_text="Mailbox actor primarily associated with this simulated persona.",
    )

    slug = models.SlugField(
        max_length=120,
        help_text="Stable identifier for prompt/runtime lookup inside the simulated tenant.",
    )
    full_name = models.CharField(max_length=255)
    first_name = models.CharField(max_length=120, blank=True)
    last_name = models.CharField(max_length=120, blank=True)
    job_title = models.CharField(max_length=255, blank=True)
    simulated_company_name = models.CharField(max_length=255, blank=True)
    seniority = models.CharField(
        max_length=32,
        choices=Seniority.choices,
        default=Seniority.MID,
    )

    notes = models.TextField(blank=True)
    character_seed = models.TextField(
        blank=True,
        help_text="Internal short seed describing the persona core.",
    )

    # Behavioral profile
    formality = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("0.50"), validators=SCALE_VALIDATORS)
    patience = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("0.50"), validators=SCALE_VALIDATORS)
    risk_tolerance = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("0.50"), validators=SCALE_VALIDATORS)
    change_openness = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("0.50"), validators=SCALE_VALIDATORS)
    cooperation = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("0.50"), validators=SCALE_VALIDATORS)
    resistance = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("0.50"), validators=SCALE_VALIDATORS)
    responsiveness = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("0.50"), validators=SCALE_VALIDATORS)
    detail_orientation = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("0.50"), validators=SCALE_VALIDATORS)

    communication_style = models.CharField(
        max_length=32,
        choices=CommunicationStyle.choices,
        default=CommunicationStyle.BALANCED,
    )
    preferred_language = models.CharField(max_length=32, default="en")
    typical_reply_latency_hours = models.PositiveIntegerField(default=24)

    # Professional context
    goals = models.JSONField(default=list, blank=True)
    pains = models.JSONField(default=list, blank=True)
    priorities = models.JSONField(default=list, blank=True)
    internal_pressures = models.JSONField(default=list, blank=True)
    budget_context = models.TextField(blank=True)
    decision_frame = models.CharField(
        max_length=32,
        choices=DecisionFrame.choices,
        default=DecisionFrame.UNKNOWN,
    )
    decision_criteria = models.JSONField(default=list, blank=True)
    blockers = models.JSONField(default=list, blank=True)

    # Dynamic state
    interest_level = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("0.30"), validators=SCALE_VALIDATORS)
    trust_level = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("0.30"), validators=SCALE_VALIDATORS)
    saturation_level = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("0.10"), validators=SCALE_VALIDATORS)
    urgency_level = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("0.20"), validators=SCALE_VALIDATORS)
    frustration_level = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("0.10"), validators=SCALE_VALIDATORS)
    relational_temperature = models.CharField(
        max_length=32,
        choices=Temperature.choices,
        default=Temperature.NEUTRAL,
    )

    last_interaction_at = models.DateTimeField(null=True, blank=True)
    state_last_updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = SimulatedPersonaQuerySet.as_manager()

    class Meta:
        ordering = ["full_name", "id"]
        unique_together = [
            ("operating_organization", "slug"),
        ]
        indexes = [
            models.Index(fields=["operating_organization", "is_active"]),
            models.Index(fields=["operating_organization", "mailbox_account"]),
            models.Index(fields=["operating_organization", "slug"]),
            models.Index(fields=["relational_temperature", "is_active"]),
        ]

    def __str__(self):
        base = self.full_name
        if self.simulated_company_name:
            return f"{base} — {self.simulated_company_name}"
        return base

    @property
    def display_company(self) -> str:
        return self.simulated_company_name or "Unknown simulated company"

    @property
    def behavioral_profile(self) -> dict:
        return {
            "formality": float(self.formality),
            "patience": float(self.patience),
            "risk_tolerance": float(self.risk_tolerance),
            "change_openness": float(self.change_openness),
            "cooperation": float(self.cooperation),
            "resistance": float(self.resistance),
            "responsiveness": float(self.responsiveness),
            "detail_orientation": float(self.detail_orientation),
            "communication_style": self.communication_style,
            "preferred_language": self.preferred_language,
            "typical_reply_latency_hours": self.typical_reply_latency_hours,
        }

    @property
    def professional_context(self) -> dict:
        return {
            "goals": self.goals or [],
            "pains": self.pains or [],
            "priorities": self.priorities or [],
            "internal_pressures": self.internal_pressures or [],
            "budget_context": self.budget_context,
            "decision_frame": self.decision_frame,
            "decision_criteria": self.decision_criteria or [],
            "blockers": self.blockers or [],
        }

    @property
    def dynamic_state(self) -> dict:
        return {
            "interest_level": float(self.interest_level),
            "trust_level": float(self.trust_level),
            "saturation_level": float(self.saturation_level),
            "urgency_level": float(self.urgency_level),
            "frustration_level": float(self.frustration_level),
            "relational_temperature": self.relational_temperature,
            "last_interaction_at": self.last_interaction_at.isoformat() if self.last_interaction_at else None,
            "state_last_updated_at": self.state_last_updated_at.isoformat() if self.state_last_updated_at else None,
        }

    def apply_state_delta(
        self,
        *,
        interest_delta=Decimal("0.00"),
        trust_delta=Decimal("0.00"),
        saturation_delta=Decimal("0.00"),
        urgency_delta=Decimal("0.00"),
        frustration_delta=Decimal("0.00"),
        relational_temperature=None,
        save=True,
    ):
        self.interest_level = self._bounded(self.interest_level + Decimal(str(interest_delta)))
        self.trust_level = self._bounded(self.trust_level + Decimal(str(trust_delta)))
        self.saturation_level = self._bounded(self.saturation_level + Decimal(str(saturation_delta)))
        self.urgency_level = self._bounded(self.urgency_level + Decimal(str(urgency_delta)))
        self.frustration_level = self._bounded(self.frustration_level + Decimal(str(frustration_delta)))

        if relational_temperature:
            self.relational_temperature = relational_temperature

        if save:
            self.save(
                update_fields=[
                    "interest_level",
                    "trust_level",
                    "saturation_level",
                    "urgency_level",
                    "frustration_level",
                    "relational_temperature",
                    "state_last_updated_at",
                    "updated_at",
                ]
            )
        return self

    @staticmethod
    def _bounded(value: Decimal) -> Decimal:
        if value < Decimal("0.00"):
            return Decimal("0.00")
        if value > Decimal("1.00"):
            return Decimal("1.00")
        return value.quantize(Decimal("0.01"))


class SimulatedPersonaMemory(models.Model):
    class MemoryKind(models.TextChoices):
        GENERAL = "general", "General"
        RELATION = "relation", "Relation"
        SALES = "sales", "Sales"
        OBJECTION = "objection", "Objection"
        INTERNAL = "internal", "Internal"

    persona = models.ForeignKey(
        SimulatedPersona,
        on_delete=models.CASCADE,
        related_name="memories",
    )
    kind = models.CharField(max_length=32, choices=MemoryKind.choices, default=MemoryKind.GENERAL)
    title = models.CharField(max_length=255)
    content = models.TextField()
    salience = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("0.50"), validators=SCALE_VALIDATORS)
    source = models.CharField(max_length=64, default="manual")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-salience", "-updated_at", "-id"]
        indexes = [
            models.Index(fields=["persona", "kind", "is_active"]),
            models.Index(fields=["persona", "salience"]),
        ]

    def __str__(self):
        return f"{self.persona.full_name} :: {self.title}"
