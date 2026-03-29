from __future__ import annotations

import json
from typing import Any

from django.conf import settings
from django.db import OperationalError, ProgrammingError

from .models import RuntimeSetting


def _read_db_setting(key: str) -> str | None:
    try:
        obj = RuntimeSetting.objects.filter(key=key).first()
    except (OperationalError, ProgrammingError):
        return None

    if obj is None:
        return None

    return obj.value


def get_runtime_setting(key: str, default: Any = None) -> Any:
    """
    Fuente de verdad en tiempo de ejecución:
    1. DB (si existe)
    2. Django settings
    3. default explícito
    """
    db_value = _read_db_setting(key)
    if db_value is not None:
        return db_value

    return getattr(settings, key, default)


def get_runtime_json_setting(key: str, default: dict | None = None) -> dict:
    fallback = default or {}
    value = get_runtime_setting(key, fallback)

    if isinstance(value, dict):
        return value

    if not isinstance(value, str):
        return fallback

    raw = value.strip()
    if not raw:
        return fallback

    try:
        parsed = json.loads(raw)
    except Exception:
        return fallback

    return parsed if isinstance(parsed, dict) else fallback


def get_runtime_str_setting(key: str, default: str = "") -> str:
    value = get_runtime_setting(key, default)
    if value is None:
        return default
    return str(value)


def get_runtime_float_setting(key: str, default: float = 0.0) -> float:
    value = get_runtime_setting(key, default)
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def get_runtime_list_setting(key: str, default: list[str] | None = None) -> list[str]:
    fallback = default or []
    value = get_runtime_setting(key, fallback)

    if isinstance(value, list):
        return [str(item) for item in value]

    if isinstance(value, tuple):
        return [str(item) for item in value]

    if not isinstance(value, str):
        return [str(item) for item in fallback]

    raw = value.strip()
    if not raw:
        return []

    try:
        parsed = json.loads(raw)
    except Exception:
        return [item.strip() for item in raw.split(",") if item.strip()]

    if isinstance(parsed, list):
        return [str(item) for item in parsed]

    return [str(item) for item in fallback]


def set_runtime_setting(key: str, value: Any) -> RuntimeSetting:
    if isinstance(value, (list, dict)):
        serialized = json.dumps(value)
    else:
        serialized = "" if value is None else str(value)

    obj, _created = RuntimeSetting.objects.update_or_create(
        key=key,
        defaults={"value": serialized},
    )
    return obj
