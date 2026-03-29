from __future__ import annotations

import json
from typing import Any

from django.contrib import admin, messages
from django.urls import reverse
from django.utils.html import format_html

from .models import ExternalActionIntent


def _coerce_json(value: Any) -> Any:
    if value in (None, ""):
        return {}
    if isinstance(value, (dict, list, tuple)):
        return value
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return {}
        try:
            return json.loads(stripped)
        except Exception:
            return {"raw": value}
    return value


def _pretty_json(value: Any) -> str:
    try:
        return json.dumps(_coerce_json(value), indent=2, ensure_ascii=False, sort_keys=True, default=str)
    except Exception:
        return str(value)


def _truncate(value: Any, limit: int = 80) -> str:
    if value in (None, ""):
        return "—"
    text = str(value).strip()
    if not text:
        return "—"
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def _extract_preview_value(intent: ExternalActionIntent, *keys: str) -> str:
    preview = _coerce_json(intent.normalized_preview)
    payload = _coerce_json(intent.payload)

    sources = [preview, payload]
    provider_context = payload.get("provider_context")
    if isinstance(provider_context, dict):
        sources.append(provider_context)

    message = payload.get("message")
    if isinstance(message, dict):
        sources.append(message)

    for source in sources:
        if not isinstance(source, dict):
            continue
        for key in keys:
            value = source.get(key)
            if value not in (None, "", [], {}, ()):
                if isinstance(value, list):
                    return ", ".join(str(item) for item in value if item)
                if isinstance(value, dict):
                    return _pretty_json(value)
                return str(value)

    return "—"


@admin.register(ExternalActionIntent)
class ExternalActionIntentAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"
    ordering = ("-created_at", "-id")
    list_per_page = 50

    list_display = (
        "public_id_display",
        "operating_organization_display",
        "mailbox_account_display",
        "intent_type_display",
        "provider_display",
        "port_name_display",
        "adapter_key_display",
        "source_display",
        "target_display",
        "approval_required_display",
        "approval_status_display",
        "dispatch_status_display",
        "execution_status_display",
        "risk_score_display",
        "confidence_display",
        "normalized_preview_compact",
        "created_at",
    )

    list_filter = (
        "operating_organization",
        "mailbox_account",
        "intent_type",
        "provider",
        "port_name",
        "approval_required",
        "approval_status",
        "dispatch_status",
        "execution_status",
        "policy_classification",
        "created_at",
    )

    search_fields = (
        "public_id",
        "idempotency_key",
        "provider",
        "port_name",
        "adapter_key",
        "source_kind",
        "source_id",
        "target_ref_type",
        "target_ref_id",
        "reason",
        "rationale",
        "last_error_code",
        "last_error_message",
        "operating_organization__name",
        "mailbox_account__email",
        "mailbox_account__account_key",
    )

    readonly_fields = (
        "public_id",
        "operating_organization",
        "mailbox_account",
        "intent_type",
        "port_name",
        "adapter_key",
        "provider",
        "target_ref_type",
        "target_ref_id",
        "source_kind",
        "source_id",
        "recommendation_link",
        "task_link",
        "requested_by",
        "approved_by",
        "approval_required",
        "approval_status",
        "dispatch_status",
        "execution_status",
        "policy_classification",
        "risk_score",
        "confidence",
        "reason",
        "rationale",
        "idempotency_key",
        "idempotency_scope",
        "dry_run_supported",
        "attempt_count",
        "last_error_code",
        "last_error_message",
        "approved_at",
        "last_attempt_at",
        "dispatched_at",
        "completed_at",
        "created_at",
        "updated_at",
        "normalized_preview_structured",
        "normalized_preview_pretty",
        "payload_pretty",
    )

    fields = (
        "public_id",
        "operating_organization",
        "mailbox_account",
        "intent_type",
        "port_name",
        "adapter_key",
        "provider",
        "target_ref_type",
        "target_ref_id",
        "source_kind",
        "source_id",
        "recommendation_link",
        "task_link",
        "requested_by",
        "approved_by",
        "approval_required",
        "approval_status",
        "dispatch_status",
        "execution_status",
        "policy_classification",
        "risk_score",
        "confidence",
        "reason",
        "rationale",
        "idempotency_key",
        "idempotency_scope",
        "dry_run_supported",
        "attempt_count",
        "last_error_code",
        "last_error_message",
        "approved_at",
        "last_attempt_at",
        "dispatched_at",
        "completed_at",
        "created_at",
        "updated_at",
        "normalized_preview_structured",
        "normalized_preview_pretty",
        "payload_pretty",
    )

    actions = (
        "approve_selected_intents",
        "dispatch_selected_intents",
    )

    @admin.display(description="public_id", ordering="public_id")
    def public_id_display(self, obj: ExternalActionIntent):
        return obj.public_id or obj.pk

    @admin.display(description="org", ordering="operating_organization")
    def operating_organization_display(self, obj: ExternalActionIntent):
        return obj.operating_organization or "—"

    @admin.display(description="mailbox", ordering="mailbox_account")
    def mailbox_account_display(self, obj: ExternalActionIntent):
        return obj.mailbox_account or "—"

    @admin.display(description="intent_type", ordering="intent_type")
    def intent_type_display(self, obj: ExternalActionIntent):
        return obj.intent_type

    @admin.display(description="provider", ordering="provider")
    def provider_display(self, obj: ExternalActionIntent):
        return obj.provider or "—"

    @admin.display(description="port", ordering="port_name")
    def port_name_display(self, obj: ExternalActionIntent):
        return obj.port_name or "—"

    @admin.display(description="adapter", ordering="adapter_key")
    def adapter_key_display(self, obj: ExternalActionIntent):
        return obj.adapter_key or "—"

    @admin.display(description="source")
    def source_display(self, obj: ExternalActionIntent):
        if obj.source_kind and obj.source_id:
            return f"{obj.source_kind}:{obj.source_id}"
        if obj.source_kind:
            return obj.source_kind
        return "—"

    @admin.display(description="target")
    def target_display(self, obj: ExternalActionIntent):
        if obj.target_ref_type and obj.target_ref_id:
            return f"{obj.target_ref_type}:{obj.target_ref_id}"
        if obj.target_ref_type:
            return obj.target_ref_type
        return "—"

    @admin.display(boolean=True, description="approval_required", ordering="approval_required")
    def approval_required_display(self, obj: ExternalActionIntent):
        return obj.approval_required

    @admin.display(description="approval", ordering="approval_status")
    def approval_status_display(self, obj: ExternalActionIntent):
        return obj.approval_status

    @admin.display(description="dispatch", ordering="dispatch_status")
    def dispatch_status_display(self, obj: ExternalActionIntent):
        return obj.dispatch_status

    @admin.display(description="execution", ordering="execution_status")
    def execution_status_display(self, obj: ExternalActionIntent):
        return obj.execution_status

    @admin.display(description="risk", ordering="risk_score")
    def risk_score_display(self, obj: ExternalActionIntent):
        if obj.risk_score is None:
            return "—"
        return obj.risk_score

    @admin.display(description="confidence", ordering="confidence")
    def confidence_display(self, obj: ExternalActionIntent):
        if obj.confidence is None:
            return "—"
        return obj.confidence

    @admin.display(description="preview")
    def normalized_preview_compact(self, obj: ExternalActionIntent):
        lines: list[str] = []

        preview_pairs = [
            ("subject", _extract_preview_value(obj, "subject", "title")),
            ("to", _extract_preview_value(obj, "to", "recipients", "to_recipients")),
            ("thread", _extract_preview_value(obj, "thread_ref", "thread_id", "conversation_id")),
            ("account", _extract_preview_value(obj, "account_key", "mailbox_email")),
            ("provider_status", _extract_preview_value(obj, "provider_status", "status")),
        ]

        for label, value in preview_pairs:
            if value != "—":
                lines.append(f"<strong>{label}</strong>: {_truncate(value, 60)}")

        if not lines:
            lines.append("<span>—</span>")

        return format_html("{}", "<br>".join(lines))

    @admin.display(description="recommendation")
    def recommendation_link(self, obj: ExternalActionIntent):
        recommendation = getattr(obj, "recommendation", None)
        if not recommendation:
            return "—"
        try:
            url = reverse(
                f"admin:{recommendation._meta.app_label}_{recommendation._meta.model_name}_change",
                args=[recommendation.pk],
            )
            return format_html('<a href="{}">{} #{}</a>', url, recommendation.__class__.__name__, recommendation.pk)
        except Exception:
            return str(recommendation)

    @admin.display(description="task")
    def task_link(self, obj: ExternalActionIntent):
        task = getattr(obj, "task", None)
        if not task:
            return "—"
        try:
            url = reverse(
                f"admin:{task._meta.app_label}_{task._meta.model_name}_change",
                args=[task.pk],
            )
            return format_html('<a href="{}">{} #{}</a>', url, task.__class__.__name__, task.pk)
        except Exception:
            return str(task)

    @admin.display(description="normalized_preview (structured)")
    def normalized_preview_structured(self, obj: ExternalActionIntent):
        preview = _coerce_json(obj.normalized_preview)
        if not isinstance(preview, dict) or not preview:
            return "—"

        rows = []
        ordered_keys = [
            "operating_organization",
            "provider",
            "provider_status",
            "account_key",
            "mailbox_email",
            "subject",
            "to",
            "recipients",
            "thread_ref",
            "thread_id",
            "conversation_id",
        ]

        seen = set()
        for key in ordered_keys:
            if key in preview and preview[key] not in (None, "", [], {}, ()):
                seen.add(key)
                rows.append((key, preview[key]))

        for key, value in preview.items():
            if key in seen or value in (None, "", [], {}, ()):
                continue
            rows.append((key, value))

        html_rows = []
        for key, value in rows:
            if isinstance(value, (dict, list)):
                rendered = _pretty_json(value)
            else:
                rendered = str(value)

            html_rows.append(
                format_html(
                    "<tr>"
                    "<th style='text-align:left; vertical-align:top; padding:6px 12px 6px 0; white-space:nowrap;'>{}</th>"
                    "<td style='padding:6px 0;'><code style='white-space:pre-wrap;'>{}</code></td>"
                    "</tr>",
                    key,
                    rendered,
                )
            )

        return format_html(
            "<table style='border-collapse:collapse;'>{}</table>",
            format_html("{}", "".join(str(row) for row in html_rows)),
        )

    @admin.display(description="normalized_preview (pretty)")
    def normalized_preview_pretty(self, obj: ExternalActionIntent):
        return format_html(
            "<pre style='white-space:pre-wrap; max-width:1200px; overflow:auto; margin:0;'>{}</pre>",
            _pretty_json(obj.normalized_preview),
        )

    @admin.display(description="payload (pretty)")
    def payload_pretty(self, obj: ExternalActionIntent):
        return format_html(
            "<pre style='white-space:pre-wrap; max-width:1200px; overflow:auto; margin:0;'>{}</pre>",
            _pretty_json(obj.payload),
        )

    @admin.action(description="Approve selected intents")
    def approve_selected_intents(self, request, queryset):
        try:
            from .services.approval import approve_external_action_intent
        except Exception:
            self.message_user(
                request,
                "No se pudo importar el servicio de aprobación.",
                level=messages.ERROR,
            )
            return

        approved = 0
        failed = 0

        for intent in queryset:
            try:
                approve_external_action_intent(intent, request.user)
                approved += 1
            except Exception:
                failed += 1

        if approved:
            self.message_user(request, f"{approved} intent(s) aprobados.", level=messages.SUCCESS)
        if failed:
            self.message_user(request, f"{failed} intent(s) fallaron durante approval.", level=messages.ERROR)

    @admin.action(description="Dispatch selected intents")
    def dispatch_selected_intents(self, request, queryset):
        dispatch_fn = None

        candidates = [
            ("apps.external_actions.services.dispatcher", "dispatch_external_action_intent"),
            ("apps.external_actions.services.dispatcher", "dispatch_intent"),
            ("apps.external_actions.dispatcher", "dispatch_external_action_intent"),
            ("apps.external_actions.dispatcher", "dispatch_intent"),
        ]

        for module_path, func_name in candidates:
            try:
                module = __import__(module_path, fromlist=[func_name])
                dispatch_fn = getattr(module, func_name, None)
                if callable(dispatch_fn):
                    break
            except Exception:
                continue

        if not callable(dispatch_fn):
            self.message_user(
                request,
                "No se encontró un dispatcher disponible.",
                level=messages.ERROR,
            )
            return

        dispatched = 0
        failed = 0

        for intent in queryset:
            try:
                dispatch_fn(intent)
                dispatched += 1
            except Exception:
                failed += 1

        if dispatched:
            self.message_user(request, f"{dispatched} intent(s) enviados al dispatcher.", level=messages.SUCCESS)
        if failed:
            self.message_user(request, f"{failed} intent(s) fallaron durante dispatch.", level=messages.ERROR)
