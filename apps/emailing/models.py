from django.db import models
from apps.companies.models import Company
from apps.contacts.models import Contact


class EmailThread(models.Model):

    external_provider = models.CharField(max_length=50, default="m365")

    external_thread_ref = models.CharField(max_length=255)

    subject = models.CharField(max_length=500)

    thread_status = models.CharField(max_length=50, default="open")

    linked_company = models.ForeignKey(
        Company,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    linked_contact = models.ForeignKey(
        Contact,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    created_at = models.DateTimeField(auto_now_add=True)


class EmailMessage(models.Model):

    thread = models.ForeignKey(
        EmailThread,
        related_name="messages",
        on_delete=models.CASCADE
    )

    external_message_ref = models.CharField(max_length=255)

    direction = models.CharField(max_length=20)

    sender = models.EmailField()

    subject = models.CharField(max_length=500)

    body_text = models.TextField(blank=True)

    sent_at = models.DateTimeField(null=True)

    message_status = models.CharField(max_length=50, default="synced")

    created_at = models.DateTimeField(auto_now_add=True)

