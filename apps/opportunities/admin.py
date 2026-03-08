from django.contrib import admin

from .models import Opportunity


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "company_name", "stage", "estimated_value", "confidence", "created_at")
    list_filter = ("stage",)
    search_fields = ("title", "company_name", "summary")
