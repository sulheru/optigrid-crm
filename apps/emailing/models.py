from django.db import models


class InboundEmail(models.Model):
    operating_organization = models.ForeignKey(
        "tenancy.OperatingOrganization",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    mailbox_account = models.ForeignKey(
        "tenancy.MailboxAccount",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    opportunity = models.ForeignKey(
        "opportunities.Opportunity",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    from_email = models.EmailField()
    subject = models.CharField(max_length=512)
    body = models.TextField()

    received_at = models.DateTimeField(auto_now_add=True)


class OutboundEmail(models.Model):
    TYPE_FOLLOWUP = "followup"
    STATUS_DRAFT = "draft"

    operating_organization = models.ForeignKey(
        "tenancy.OperatingOrganization",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    mailbox_account = models.ForeignKey(
        "tenancy.MailboxAccount",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    opportunity = models.ForeignKey(
        "opportunities.Opportunity",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    to_email = models.EmailField()
    subject = models.CharField(max_length=512)
    body = models.TextField()

    status = models.CharField(max_length=50, default=STATUS_DRAFT)
    email_type = models.CharField(max_length=50, default=TYPE_FOLLOWUP)

    created_at = models.DateTimeField(auto_now_add=True)
