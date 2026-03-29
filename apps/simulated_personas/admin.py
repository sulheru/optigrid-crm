from django.contrib import admin

from .models import SimulatedPersona, SimulatedPersonaMemory


class SimulatedPersonaMemoryInline(admin.TabularInline):
    model = SimulatedPersonaMemory
    extra = 0
    fields = ("kind", "title", "salience", "source", "is_active")
    ordering = ("-salience", "-updated_at")


@admin.register(SimulatedPersona)
class SimulatedPersonaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "full_name",
        "simulated_company_name",
        "job_title",
        "seniority",
        "operating_organization",
        "mailbox_account",
        "relational_temperature",
        "interest_level",
        "trust_level",
        "is_active",
        "updated_at",
    )
    list_filter = (
        "operating_organization",
        "mailbox_account",
        "seniority",
        "communication_style",
        "decision_frame",
        "relational_temperature",
        "is_active",
    )
    search_fields = (
        "full_name",
        "first_name",
        "last_name",
        "job_title",
        "simulated_company_name",
        "slug",
        "notes",
        "character_seed",
    )
    readonly_fields = ("created_at", "updated_at", "state_last_updated_at")
    prepopulated_fields = {"slug": ("full_name",)}
    inlines = [SimulatedPersonaMemoryInline]

    fieldsets = (
        (
            "Tenant scope",
            {
                "fields": (
                    "operating_organization",
                    "mailbox_account",
                    "slug",
                    "is_active",
                )
            },
        ),
        (
            "Identity",
            {
                "fields": (
                    "full_name",
                    "first_name",
                    "last_name",
                    "job_title",
                    "simulated_company_name",
                    "seniority",
                    "notes",
                    "character_seed",
                )
            },
        ),
        (
            "Behavioral profile",
            {
                "fields": (
                    "communication_style",
                    "preferred_language",
                    "typical_reply_latency_hours",
                    "formality",
                    "patience",
                    "risk_tolerance",
                    "change_openness",
                    "cooperation",
                    "resistance",
                    "responsiveness",
                    "detail_orientation",
                )
            },
        ),
        (
            "Professional context",
            {
                "fields": (
                    "goals",
                    "pains",
                    "priorities",
                    "internal_pressures",
                    "budget_context",
                    "decision_frame",
                    "decision_criteria",
                    "blockers",
                )
            },
        ),
        (
            "Dynamic state",
            {
                "fields": (
                    "interest_level",
                    "trust_level",
                    "saturation_level",
                    "urgency_level",
                    "frustration_level",
                    "relational_temperature",
                    "last_interaction_at",
                    "state_last_updated_at",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )


@admin.register(SimulatedPersonaMemory)
class SimulatedPersonaMemoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "persona",
        "kind",
        "title",
        "salience",
        "source",
        "is_active",
        "updated_at",
    )
    list_filter = ("kind", "source", "is_active", "persona__operating_organization")
    search_fields = ("persona__full_name", "title", "content")
    readonly_fields = ("created_at", "updated_at")
