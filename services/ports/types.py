from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ValidationResult:
    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass(slots=True)
class PreparedAction:
    provider_payload: dict[str, Any]
    preview: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ProviderResult:
    status: str
    provider_id: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)
    error_code: str | None = None
    error_message: str | None = None
    retryable: bool = False


@dataclass(slots=True)
class NormalizedExternalResult:
    status: str
    external_ref: str | None = None
    provider_id: str | None = None
    summary: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)
    retryable: bool = False
    error_code: str | None = None


@dataclass(slots=True)
class PolicyDecision:
    decision: str
    classification: str
    reasons: list[str] = field(default_factory=list)
    requires_approval: bool = False
    policy_snapshot: dict[str, Any] = field(default_factory=dict)
