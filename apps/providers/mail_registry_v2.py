from __future__ import annotations

from apps.providers.mail_embedded import EmbeddedMailProvider
from apps.providers.mail_m365 import M365MailProvider


_PROVIDER_MAP = {
    "embedded": EmbeddedMailProvider,
    "m365": M365MailProvider,
}


def get_mail_provider_by_key(provider_key: str):
    try:
        provider_cls = _PROVIDER_MAP[provider_key]
    except KeyError as exc:
        raise ValueError(f"Unknown mail provider: {provider_key}") from exc
    return provider_cls()
