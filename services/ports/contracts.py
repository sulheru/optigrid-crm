from __future__ import annotations

from abc import ABC, abstractmethod

from services.ports.types import (
    NormalizedExternalResult,
    PreparedAction,
    ProviderResult,
    ValidationResult,
)


class ExternalPort(ABC):
    adapter_key: str = ""
    port_name: str = ""
    provider: str = ""

    @abstractmethod
    def validate(self, intent) -> ValidationResult:
        raise NotImplementedError

    @abstractmethod
    def prepare(self, intent) -> PreparedAction:
        raise NotImplementedError

    @abstractmethod
    def dry_run(self, intent) -> NormalizedExternalResult:
        raise NotImplementedError

    @abstractmethod
    def execute(self, prepared_action: PreparedAction) -> ProviderResult:
        raise NotImplementedError

    @abstractmethod
    def normalize_result(self, provider_result: ProviderResult) -> NormalizedExternalResult:
        raise NotImplementedError

    @abstractmethod
    def compute_idempotency(self, intent) -> str:
        raise NotImplementedError
