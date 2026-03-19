from __future__ import annotations

from typing import Any, List, Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator


ALLOWED_SIGNAL_TYPES = {"funding", "hiring", "expansion", "growth", "tech", "trigger"}
ALLOWED_EMPLOYEE_RANGES = {
    "1-10",
    "11-50",
    "51-200",
    "201-500",
    "501-1000",
    "1001-5000",
    "5000+",
    "unknown",
}
ALLOWED_HYPOTHESIS_TYPES = {
    "network_refresh",
    "observability_need",
    "security_upgrade",
    "cloud_transition",
    "automation_need",
    "managed_services_fit",
}
ALLOWED_RATIONALE_CODES = {
    "dach_presence",
    "mid_market_fit",
    "infra_complexity",
    "recent_growth",
    "active_hiring",
    "expansion_signal",
    "timing_good",
    "industry_fit",
    "high_actionability",
}


class LeadSignalSchema(BaseModel):
    signal_type: str
    signal_value: str = ""
    confidence: float = Field(ge=0.0, le=1.0)
    source_ref: str = ""
    observed_at: Optional[str] = None
    payload: dict[str, Any] = Field(default_factory=dict)

    @field_validator("signal_type")
    @classmethod
    def validate_signal_type(cls, value: str) -> str:
        if value not in ALLOWED_SIGNAL_TYPES:
            raise ValueError(f"signal_type inválido: {value}")
        return value


class LeadDiscoveryItemSchema(BaseModel):
    company_name: str = Field(min_length=2, max_length=255)
    website: Optional[HttpUrl] = None
    country: str = Field(default="", max_length=100)
    city: str = Field(default="", max_length=100)
    industry: str = Field(default="", max_length=100)
    employee_range: str = Field(default="unknown")
    fit_score: float = Field(ge=0.0, le=1.0)
    timing_score: float = Field(ge=0.0, le=1.0)
    novelty_score: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    rationale_codes: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    signals: List[LeadSignalSchema] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("employee_range")
    @classmethod
    def validate_employee_range(cls, value: str) -> str:
        if value not in ALLOWED_EMPLOYEE_RANGES:
            raise ValueError(f"employee_range inválido: {value}")
        return value

    @field_validator("rationale_codes")
    @classmethod
    def validate_rationale_codes(cls, values: List[str]) -> List[str]:
        invalid = [v for v in values if v not in ALLOWED_RATIONALE_CODES]
        if invalid:
            raise ValueError(f"rationale_codes inválidos: {invalid}")
        return values


class LeadDiscoveryBatchSchema(BaseModel):
    query: str
    items: List[LeadDiscoveryItemSchema] = Field(default_factory=list)


class LeadEnrichmentSchema(BaseModel):
    company_name: str = Field(min_length=2, max_length=255)
    website: Optional[HttpUrl] = None
    primary_country: str = Field(default="", max_length=100)
    regions: List[str] = Field(default_factory=list)
    industry: str = Field(default="", max_length=100)
    employee_range: str = Field(default="unknown")
    infra_complexity_level: int = Field(ge=1, le=5)
    stack_signals: List[str] = Field(default_factory=list)
    buyer_roles: List[str] = Field(default_factory=list)
    pain_codes: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)

    @field_validator("employee_range")
    @classmethod
    def validate_employee_range(cls, value: str) -> str:
        if value not in ALLOWED_EMPLOYEE_RANGES:
            raise ValueError(f"employee_range inválido: {value}")
        return value


class LeadHypothesisSchema(BaseModel):
    company_name: str = Field(min_length=2, max_length=255)
    hypothesis_type: str
    timing_label: str = Field(pattern="^(now|soon|later)$")
    fit_label: str = Field(pattern="^(low|medium|high)$")
    actionability_label: str = Field(pattern="^(low|medium|high)$")
    why_now_codes: List[str] = Field(default_factory=list)
    probable_problem_codes: List[str] = Field(default_factory=list)
    recommended_next_action: str = Field(
        pattern="^(research_more|watchlist|approve_for_enrichment|dismiss)$"
    )
    confidence: float = Field(ge=0.0, le=1.0)

    @field_validator("hypothesis_type")
    @classmethod
    def validate_hypothesis_type(cls, value: str) -> str:
        if value not in ALLOWED_HYPOTHESIS_TYPES:
            raise ValueError(f"hypothesis_type inválido: {value}")
        return value
