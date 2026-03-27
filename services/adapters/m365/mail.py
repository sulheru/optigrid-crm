from __future__ import annotations

from services.ports.contracts import ExternalPort
from services.ports.idempotency import build_intent_idempotency_key
from services.ports.types import (
    NormalizedExternalResult,
    PreparedAction,
    ProviderResult,
    ValidationResult,
)


class M365MailPort(ExternalPort):
    adapter_key = "m365.mail"
    port_name = "mail"
    provider = "m365"

    def validate(self, intent) -> ValidationResult:
        payload = intent.payload or {}
        errors: list[str] = []

        if intent.intent_type not in {"email.create_draft", "email.send"}:
            errors.append(f"Unsupported mail intent: {intent.intent_type}")

        recipients = payload.get("to") or []
        if not recipients:
            errors.append("payload.to is required")

        if not payload.get("subject"):
            errors.append("payload.subject is required")

        return ValidationResult(ok=not errors, errors=errors)

    def prepare(self, intent) -> PreparedAction:
        payload = intent.payload or {}
        preview = {
            "type": intent.intent_type,
            "to": payload.get("to", []),
            "cc": payload.get("cc", []),
            "bcc": payload.get("bcc", []),
            "subject": payload.get("subject", ""),
            "body_preview": (payload.get("body", "") or "")[:500],
        }
        return PreparedAction(provider_payload=payload, preview=preview)

    def dry_run(self, intent) -> NormalizedExternalResult:
        prepared = self.prepare(intent)
        return NormalizedExternalResult(
            status="dry_run",
            summary="Dry run completed successfully.",
            raw=prepared.preview,
        )

    def execute(self, prepared_action: PreparedAction) -> ProviderResult:
        # Slice V1:
        # - create_draft queda implementado como provider-ready payload
        # - send queda disponible para ejecución real solo cuando se conecte el provider
        payload = prepared_action.provider_payload or {}

        if payload.get("__simulate_failure__"):
            return ProviderResult(
                status="failed",
                error_code="simulated_failure",
                error_message="Simulated provider failure.",
                retryable=False,
            )

        return ProviderResult(
            status="succeeded",
            provider_id="m365-placeholder",
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
                summary="Mail action accepted by adapter.",
                raw=provider_result.raw,
            )

        return NormalizedExternalResult(
            status="failed",
            provider_id=provider_result.provider_id,
            summary=provider_result.error_message or "Mail action failed.",
            raw=provider_result.raw,
            retryable=provider_result.retryable,
            error_code=provider_result.error_code,
        )

    def compute_idempotency(self, intent) -> str:
        return build_intent_idempotency_key(intent)
