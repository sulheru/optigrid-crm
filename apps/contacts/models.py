from django.db import models
from apps.companies.models import Company


class Contact(models.Model):

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="contacts"
    )

    full_name = models.CharField(max_length=255)

    job_title = models.CharField(max_length=255, blank=True)

    email = models.EmailField(blank=True, null=True)

    email_status = models.CharField(max_length=50, default="not_found")

    linkedin_url = models.URLField(blank=True, null=True)

    contact_status = models.CharField(max_length=50, default="identified")

    confidence = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name

