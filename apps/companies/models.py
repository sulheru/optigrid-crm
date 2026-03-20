# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/companies/models.py
from django.db import models


class Company(models.Model):

    legal_name = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255, blank=True)

    website = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)

    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)

    industry = models.CharField(max_length=100, blank=True)

    company_status = models.CharField(max_length=50, default="discovered")

    fit_score = models.FloatField(null=True, blank=True)

    source = models.CharField(max_length=100, blank=True)

    confidence = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.legal_name

