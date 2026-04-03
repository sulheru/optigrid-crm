from __future__ import annotations

from typing import Any

from apps.core.runtime_settings import get_runtime_json_setting
from apps.providers.mail_provider import MailAccountRef
from apps.tenancy.models import MailboxAccount


DEFAULT_MAIL_PROVIDER_SETTINGS: dict[str, Any] = {
    "default_provider": "embedded",
    "default_account": "default",
    "accounts": {
        "default": {
            "provider": "embedded",
            "mailbox": None,
            "display_name": "Primary mailbox",
            "enabled": True,
            "can_create_draft": True,
            "can_send": False,
            "metadata": {},
        }
    },
}


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def get_mail_provider_settings() -> dict[str, Any]:
    override = get_runtime_json_setting("mail_provider", {})
    return _deep_merge(DEFAULT_MAIL_PROVIDER_SETTINGS, override)


def resolve_mail_account_ref(mailbox_account: MailboxAccount | int) -> MailAccountRef:
    if isinstance(mailbox_account, int):
        mailbox_account = MailboxAccount.objects.select_related("operating_organization").get(
            pk=mailbox_account
        )

    if mailbox_account.status != MailboxAccount.Status.ACTIVE:
        raise ValueError(f"Mailbox account '{mailbox_account.pk}' is not active")

    metadata = dict(mailbox_account.metadata or {})
    metadata.setdefault("mailbox_account_id", mailbox_account.id)
    metadata.setdefault("operating_organization_id", mailbox_account.operating_organization_id)

    return MailAccountRef(
        provider=mailbox_account.provider,
        account_key=mailbox_account.account_key,
        mailbox=mailbox_account.email,
        display_name=mailbox_account.display_name or mailbox_account.email,
        metadata=metadata,
    )


def resolve_mail_account(account_key: str | None = None) -> MailAccountRef:
    settings = get_mail_provider_settings()
    accounts = settings.get("accounts") or {}
    selected_key = account_key or settings.get("default_account") or "default"

    if selected_key not in accounts:
        raise ValueError(f"Mail account '{selected_key}' is not configured")

    selected = accounts[selected_key] or {}

    if not selected.get("enabled", True):
        raise ValueError(f"Mail account '{selected_key}' is disabled")

    if not selected.get("can_create_draft", True):
        raise ValueError(f"Mail account '{selected_key}' cannot create drafts")

    return MailAccountRef(
        provider=selected.get("provider") or settings.get("default_provider") or "embedded",
        account_key=selected_key,
        mailbox=selected.get("mailbox"),
        display_name=selected.get("display_name"),
        metadata=selected.get("metadata") or {},
    )
