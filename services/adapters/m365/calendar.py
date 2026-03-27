from __future__ import annotations

from services.ports.contracts import ExternalPort
from services.ports.idempotency import build_intent_idempotency_key
from services.ports.types import (
    NormalizedExternalResult,
    PreparedAction,
    ProviderResult,
    ValidationResult,
)


class M365CalendarPort(ExternalPort):
    adapter_key = "m365.calendar"
    port_name = "calendar"
    provider = "m365"

    def validate(self, intent) -> ValidationResult:
        payload = intent.payload or {}
        errors: list[str] = []

        if intent.intent_type not in {"calendar.create_event", "calendar.update_event"}:
            errors.append(f"Unsupported calendar intent: {intent.intent_type}")

        if not payload.get("subject"):
            errors.append("payload.subject is required")

        if not payload.get("start"):
            errors.append("payload.start is required")

        if not payload.get("end"):
            errors.append("payload.end is required")

        return ValidationResult(ok=not errors, errors=errors)

    def prepare(self, intent) -> PreparedAction:
        payload = intent.payload or {}
        preview = {
            "type": intent.intent_type,
            "subject": payload.get("subject", ""),
            "start": payload.get("start"),
            "end": payload.get("end"),
            "attendees": payload.get("attendees", []),
            "location": payload.get("location", ""),
        }
        return PreparedAction(provider_payload=payload, preview=preview)

    def dry_run(self, intent) -> NormalizedExternalResult:
        prepared = self.prepare(intent)
        return NormalizedExternalResult(
            status="dry_run",
            summary="Calendar dry run completed successfully.",
            raw=prepared.preview,
        )

    def execute(self, prepared_action: PreparedAction) -> ProviderResult:
        payload = prepared_action.provider_payload or {}
        return ProviderResult(
            status="succeeded",
            provider_id="m365-calendar-placeholder",
            raw={
                "provider": "m365",
                "adapter": self.adapter_key,
                "provider_payload": payload,
                "mode": "provider_ready",
            },
        )

    def normalize_result(self, provider_result: ProviderResult) -> NormalizedExternalResult:
        if provider_result.status == "succeeded":
            return NormalizedExternalResult(
                status="succeeded",
                provider_id=provider_result.provider_id,
                summary="Calendar action accepted by adapter.",
                raw=provider_result.raw,
            )

        return NormalizedExternalResult(
            status="failed",
            provider_id=provider_result.provider_id,
            summary=provider_result.error_message or "Calendar action failed.",
            raw=provider_result.raw,
            retryable=provider_result.retryable,
            error_code=provider_result.error_code,
        )

    def compute_idempotency(self, intent) -> str:
        return build_intent_idempotency_key(intent)
