from django.core.exceptions import ValidationError
from django.db import models


class OutboundEmail(models.Model):
    TYPE_FIRST_CONTACT = "first_contact"
    TYPE_FOLLOWUP = "followup"

    TYPE_CHOICES = [
        (TYPE_FIRST_CONTACT, "First contact"),
        (TYPE_FOLLOWUP, "Follow-up"),
    ]

    STATUS_DRAFT = "draft"
    STATUS_APPROVED = "approved"
    STATUS_SENT = "sent"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_SENT, "Sent"),
        (STATUS_FAILED, "Failed"),
    ]

    operating_organization = models.ForeignKey(
        "tenancy.OperatingOrganization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="outbound_emails",
    )

    mailbox_account = models.ForeignKey(
        "tenancy.MailboxAccount",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="outbound_emails",
    )

    opportunity = models.ForeignKey(
        "opportunities.Opportunity",
        on_delete=models.CASCADE,
        related_name="outbound_emails",
    )

    source_inbound = models.ForeignKey(
        "emailing.InboundEmail",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generated_followups",
    )

    source_recommendation = models.ForeignKey(
        "recommendations.AIRecommendation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generated_outbound_emails",
    )

    email_type = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES,
        default=TYPE_FIRST_CONTACT,
    )

    to_email = models.CharField(max_length=255, blank=True, default="")
    subject = models.CharField(max_length=255)
    body = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
    )

    generated_by = models.CharField(max_length=50, default="ai")

    approved_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    failure_reason = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        super().clean()

        if self.mailbox_account_id is None:
            return

        mailbox_account = self.mailbox_account
        mailbox_org_id = mailbox_account.operating_organization_id

        if self.operating_organization_id is None:
            self.operating_organization_id = mailbox_org_id
        elif self.operating_organization_id != mailbox_org_id:
            raise ValidationError(
                {
                    "operating_organization": (
                        "operating_organization must match mailbox_account.operating_organization."
                    )
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.subject} [{self.status}] [{self.email_type}]"


class InboundEmail(models.Model):
    STATUS_NEW = "new"
    STATUS_REVIEWED = "reviewed"
    STATUS_LINKED = "linked"

    STATUS_CHOICES = [
        (STATUS_NEW, "New"),
        (STATUS_REVIEWED, "Reviewed"),
        (STATUS_LINKED, "Linked"),
    ]

    REPLY_INTERESTED = "interested"
    REPLY_NOT_NOW = "not_now"
    REPLY_NOT_INTERESTED = "not_interested"
    REPLY_NEEDS_INFO = "needs_info"
    REPLY_UNCLEAR = "unclear"

    REPLY_TYPE_CHOICES = [
        (REPLY_INTERESTED, "Interested"),
        (REPLY_NOT_NOW, "Not now"),
        (REPLY_NOT_INTERESTED, "Not interested"),
        (REPLY_NEEDS_INFO, "Needs info"),
        (REPLY_UNCLEAR, "Unclear"),
    ]

    operating_organization = models.ForeignKey(
        "tenancy.OperatingOrganization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inbound_emails",
    )

    mailbox_account = models.ForeignKey(
        "tenancy.MailboxAccount",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inbound_emails",
    )

    opportunity = models.ForeignKey(
        "opportunities.Opportunity",
        on_delete=models.CASCADE,
        related_name="inbound_emails",
    )

    source_outbound = models.ForeignKey(
        "emailing.OutboundEmail",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="simulated_replies",
    )

    from_email = models.CharField(max_length=255, blank=True, default="")
    subject = models.CharField(max_length=255)
    body = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NEW,
    )

    reply_type = models.CharField(
        max_length=30,
        choices=REPLY_TYPE_CHOICES,
        default=REPLY_UNCLEAR,
    )

    received_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-received_at", "-created_at"]

    def clean(self):
        super().clean()

        if self.mailbox_account_id is None:
            raise ValidationError(
                {"mailbox_account": "InboundEmail requires canonical mailbox_account."}
            )

        mailbox_account = self.mailbox_account
        mailbox_org_id = mailbox_account.operating_organization_id

        if self.operating_organization_id is None:
            self.operating_organization_id = mailbox_org_id
        elif self.operating_organization_id != mailbox_org_id:
            raise ValidationError(
                {
                    "operating_organization": (
                        "operating_organization must match mailbox_account.operating_organization."
                    )
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.subject} [{self.reply_type}]"


class InboundInterpretation(models.Model):
    INTENT_INTERESTED = "interested"
    INTENT_OBJECTION = "objection"
    INTENT_DELAY = "delay"
    INTENT_REJECTION = "rejection"
    INTENT_UNCLEAR = "unclear"

    INTENT_CHOICES = [
        (INTENT_INTERESTED, "Interested"),
        (INTENT_OBJECTION, "Objection / Needs info"),
        (INTENT_DELAY, "Delay / Not now"),
        (INTENT_REJECTION, "Rejection"),
        (INTENT_UNCLEAR, "Unclear"),
    ]

    URGENCY_LOW = "low"
    URGENCY_MEDIUM = "medium"
    URGENCY_HIGH = "high"

    URGENCY_CHOICES = [
        (URGENCY_LOW, "Low"),
        (URGENCY_MEDIUM, "Medium"),
        (URGENCY_HIGH, "High"),
    ]

    SENTIMENT_POSITIVE = "positive"
    SENTIMENT_NEUTRAL = "neutral"
    SENTIMENT_NEGATIVE = "negative"

    SENTIMENT_CHOICES = [
        (SENTIMENT_POSITIVE, "Positive"),
        (SENTIMENT_NEUTRAL, "Neutral"),
        (SENTIMENT_NEGATIVE, "Negative"),
    ]

    ACTION_ADVANCE_OPPORTUNITY = "advance_opportunity"
    ACTION_SEND_INFORMATION = "send_information"
    ACTION_SCHEDULE_FOLLOWUP = "schedule_followup"
    ACTION_MARK_LOST = "mark_lost"
    ACTION_SEND_CLARIFICATION = "send_clarification"

    ACTION_CHOICES = [
        (ACTION_ADVANCE_OPPORTUNITY, "Advance opportunity"),
        (ACTION_SEND_INFORMATION, "Send information"),
        (ACTION_SCHEDULE_FOLLOWUP, "Schedule follow-up"),
        (ACTION_MARK_LOST, "Mark lost"),
        (ACTION_SEND_CLARIFICATION, "Send clarification"),
    ]

    inbound_email = models.OneToOneField(
        "emailing.InboundEmail",
        on_delete=models.CASCADE,
        related_name="ai_interpretation",
    )

    intent = models.CharField(
        max_length=32,
        choices=INTENT_CHOICES,
        default=INTENT_UNCLEAR,
    )
    urgency = models.CharField(
        max_length=16,
        choices=URGENCY_CHOICES,
        default=URGENCY_MEDIUM,
    )
    sentiment = models.CharField(
        max_length=16,
        choices=SENTIMENT_CHOICES,
        default=SENTIMENT_NEUTRAL,
    )
    recommended_action = models.CharField(
        max_length=32,
        choices=ACTION_CHOICES,
        default=ACTION_SEND_CLARIFICATION,
    )

    confidence = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    rationale = models.TextField(blank=True, default="")
    signals_json = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"InboundInterpretation("
            f"inbound_id={self.inbound_email_id}, "
            f"intent={self.intent}, "
            f"action={self.recommended_action}"
            f")"
        )


class InboundDecision(models.Model):
    STATUS_SUGGESTED = "suggested"
    STATUS_APPLIED = "applied"
    STATUS_DISMISSED = "dismissed"

    STATUS_CHOICES = [
        (STATUS_SUGGESTED, "Suggested"),
        (STATUS_APPLIED, "Applied"),
        (STATUS_DISMISSED, "Dismissed"),
    ]

    PRIORITY_LOW = "low"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_HIGH = "high"

    PRIORITY_CHOICES = [
        (PRIORITY_LOW, "Low"),
        (PRIORITY_MEDIUM, "Medium"),
        (PRIORITY_HIGH, "High"),
    ]

    ACTION_ADVANCE_OPPORTUNITY = InboundInterpretation.ACTION_ADVANCE_OPPORTUNITY
    ACTION_SEND_INFORMATION = InboundInterpretation.ACTION_SEND_INFORMATION
    ACTION_SCHEDULE_FOLLOWUP = InboundInterpretation.ACTION_SCHEDULE_FOLLOWUP
    ACTION_MARK_LOST = InboundInterpretation.ACTION_MARK_LOST
    ACTION_SEND_CLARIFICATION = InboundInterpretation.ACTION_SEND_CLARIFICATION

    ACTION_CHOICES = InboundInterpretation.ACTION_CHOICES

    inbound_email = models.ForeignKey(
        "emailing.InboundEmail",
        on_delete=models.CASCADE,
        related_name="ai_decisions",
    )

    interpretation = models.ForeignKey(
        "emailing.InboundInterpretation",
        on_delete=models.CASCADE,
        related_name="decisions",
    )

    action_type = models.CharField(
        max_length=32,
        choices=ACTION_CHOICES,
    )
    status = models.CharField(
        max_length=16,
        choices=STATUS_CHOICES,
        default=STATUS_SUGGESTED,
    )

    summary = models.CharField(max_length=255, blank=True, default="")
    payload_json = models.JSONField(default=dict, blank=True)
    requires_approval = models.BooleanField(default=True)

    score = models.FloatField(default=0.0)
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default=PRIORITY_MEDIUM,
    )
    risk_flags = models.JSONField(default=list, blank=True)

    applied_automatically = models.BooleanField(default=False)
    automation_reason = models.CharField(max_length=255, blank=True, default="")

    applied_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"InboundDecision("
            f"inbound_id={self.inbound_email_id}, "
            f"action={self.action_type}, "
            f"status={self.status}"
            f")"
        )
