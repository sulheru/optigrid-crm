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

    def __str__(self):
        return f"{self.subject} [{self.reply_type}]"
