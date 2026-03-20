# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/lead_research/services/signal_discovery.py
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Iterable
from urllib.parse import urlparse

from django.conf import settings
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.utils import timezone
from pydantic import ValidationError

from apps.companies.models import Company
from apps.lead_research.models import LeadResearchSnapshot, LeadSignal, LeadSuggestion
from apps.lead_research.schemas import (
    LeadDiscoveryBatchSchema,
    LeadDiscoveryItemSchema,
    LeadEnrichmentSchema,
    LeadHypothesisSchema,
)

logger = logging.getLogger(__name__)


@dataclass
class DiscoveryRunResult:
    queries: list[str]
    processed: int = 0
    created: int = 0
    updated: int = 0
    skipped_existing_company: int = 0
    skipped_existing_suggestion: int = 0
    skipped_dismissed: int = 0
    validation_errors: int = 0


class SignalDiscoveryService:
    DEFAULT_QUERIES = [
        "DACH mid-market companies with infrastructure growth signals",
        "Companies hiring network cloud security infrastructure in Germany Austria Switzerland",
        "Recent expansion or funding signals in industrial and B2B software companies in DACH",
    ]

    def run(self, queries: list[str] | None = None) -> DiscoveryRunResult:
        queries = queries or self.generate_queries()
        result = DiscoveryRunResult(queries=queries)

        for query in queries:
            raw_payload = self._call_backend(query=query)
            batch = self._parse_batch(raw_payload=raw_payload, query=query)
            if not batch:
                continue

            for item in batch.items:
                result.processed += 1
                outcome = self._persist_item(item=item, source_query=query)
                if outcome == "created":
                    result.created += 1
                elif outcome == "updated":
                    result.updated += 1
                elif outcome == "skip_existing_company":
                    result.skipped_existing_company += 1
                elif outcome == "skip_existing_suggestion":
                    result.skipped_existing_suggestion += 1
                elif outcome == "skip_dismissed":
                    result.skipped_dismissed += 1
                elif outcome == "validation_error":
                    result.validation_errors += 1

        logger.info(
            "lead_research.discovery.finished queries=%s processed=%s created=%s updated=%s "
            "skip_company=%s skip_suggestion=%s skip_dismissed=%s validation_errors=%s",
            len(result.queries),
            result.processed,
            result.created,
            result.updated,
            result.skipped_existing_company,
            result.skipped_existing_suggestion,
            result.skipped_dismissed,
            result.validation_errors,
        )
        return result

    def generate_queries(self) -> list[str]:
        custom_queries = getattr(settings, "LEAD_RESEARCH_DISCOVERY_QUERIES", None)
        if custom_queries:
            return [str(q).strip() for q in custom_queries if str(q).strip()]
        return list(self.DEFAULT_QUERIES)

    def _parse_batch(self, raw_payload: str | dict[str, Any], query: str) -> LeadDiscoveryBatchSchema | None:
        try:
            payload = self._coerce_json(raw_payload)
            payload.setdefault("query", query)
            return LeadDiscoveryBatchSchema.model_validate(payload)
        except ValidationError:
            logger.exception("lead_research.discovery.batch_validation_error query=%s", query)
            return None
        except Exception:
            logger.exception("lead_research.discovery.batch_parse_error query=%s", query)
            return None

    def _persist_item(self, item: LeadDiscoveryItemSchema, source_query: str) -> str:
        normalized_name = normalize_company_name(item.company_name)
        website = str(item.website) if item.website else ""
        domain = extract_domain(website)

        if self._is_existing_company(company_name=item.company_name, normalized_name=normalized_name, domain=domain):
            return "skip_existing_company"

        existing = LeadSuggestion.objects.filter(
            normalized_company_name=normalized_name,
            website_domain=domain,
        ).first()

        if existing and existing.status == LeadSuggestion.STATUS_DISMISSED:
            return "skip_dismissed"

        try:
            with transaction.atomic():
                suggestion, created = LeadSuggestion.objects.get_or_create(
                    normalized_company_name=normalized_name,
                    website_domain=domain,
                    defaults={
                        "company_name": item.company_name,
                        "website": website,
                        "country": item.country,
                        "city": item.city,
                        "industry": item.industry,
                        "employee_range": item.employee_range,
                        "fit_score": to_decimal(item.fit_score),
                        "timing_score": to_decimal(item.timing_score),
                        "novelty_score": to_decimal(item.novelty_score),
                        "confidence": to_decimal(item.confidence),
                        "source_query": source_query,
                        "source_provider": "gemini_mock",
                        "rationale_codes": list(item.rationale_codes),
                        "tags": list(item.tags),
                        "metadata": dict(item.metadata),
                    },
                )

                if not created:
                    if suggestion.status == LeadSuggestion.STATUS_DISMISSED:
                        return "skip_dismissed"

                    changed = False
                    for attr, value in {
                        "company_name": item.company_name,
                        "website": website,
                        "country": item.country,
                        "city": item.city,
                        "industry": item.industry,
                        "employee_range": item.employee_range,
                        "fit_score": to_decimal(item.fit_score),
                        "timing_score": to_decimal(item.timing_score),
                        "novelty_score": to_decimal(item.novelty_score),
                        "confidence": to_decimal(item.confidence),
                        "source_query": source_query,
                        "rationale_codes": list(item.rationale_codes),
                        "tags": list(item.tags),
                        "metadata": dict(item.metadata),
                        "last_seen_at": timezone.now(),
                    }.items():
                        if getattr(suggestion, attr) != value:
                            setattr(suggestion, attr, value)
                            changed = True
                    if changed:
                        suggestion.save()

                self._replace_signals(suggestion=suggestion, signals=item.signals)
                self._upsert_snapshot(
                    suggestion=suggestion,
                    discovery_payload=item.model_dump(mode="json"),
                )
                return "created" if created else "updated"
        except IntegrityError:
            logger.warning(
                "lead_research.discovery.integrity_conflict company=%s domain=%s",
                item.company_name,
                domain,
            )
            return "skip_existing_suggestion"
        except ValidationError:
            logger.exception("lead_research.discovery.item_validation_error company=%s", item.company_name)
            return "validation_error"
        except Exception:
            logger.exception("lead_research.discovery.persist_error company=%s", item.company_name)
            return "validation_error"

    def _replace_signals(self, suggestion: LeadSuggestion, signals: Iterable[Any]) -> None:
        suggestion.signals.all().delete()
        signal_objects = []
        for signal in signals:
            signal_objects.append(
                LeadSignal(
                    suggestion=suggestion,
                    signal_type=signal.signal_type,
                    signal_value=signal.signal_value,
                    confidence=to_decimal(signal.confidence),
                    source_provider="gemini_mock",
                    source_ref=signal.source_ref,
                    observed_at=parse_datetime_or_none(signal.observed_at),
                    payload=dict(signal.payload or {}),
                )
            )
        if signal_objects:
            LeadSignal.objects.bulk_create(signal_objects)

    def _upsert_snapshot(self, suggestion: LeadSuggestion, discovery_payload: dict[str, Any]) -> None:
        enrichment_payload = self._build_enrichment_payload(discovery_payload)
        hypothesis_payload = self._build_hypothesis_payload(discovery_payload)

        LeadResearchSnapshot.objects.update_or_create(
            suggestion=suggestion,
            defaults={
                "discovery_payload": discovery_payload,
                "enrichment_payload": enrichment_payload,
                "hypothesis_payload": hypothesis_payload,
                "summary_codes": discovery_payload.get("rationale_codes", []),
                "model_name": "gemini_mock",
                "prompt_version": "v1",
            },
        )

    def _build_enrichment_payload(self, discovery_payload: dict[str, Any]) -> dict[str, Any]:
        enrichment = LeadEnrichmentSchema(
            company_name=discovery_payload["company_name"],
            website=discovery_payload.get("website"),
            primary_country=discovery_payload.get("country", ""),
            regions=[discovery_payload.get("country", "")] if discovery_payload.get("country") else [],
            industry=discovery_payload.get("industry", ""),
            employee_range=discovery_payload.get("employee_range", "unknown"),
            infra_complexity_level=4 if "infra_complexity" in discovery_payload.get("rationale_codes", []) else 3,
            stack_signals=discovery_payload.get("tags", []),
            buyer_roles=["Head of IT", "Infrastructure Lead", "CTO"],
            pain_codes=discovery_payload.get("rationale_codes", []),
            confidence=min(float(discovery_payload.get("confidence", 0.0)), 1.0),
        )
        return enrichment.model_dump(mode="json")

    def _build_hypothesis_payload(self, discovery_payload: dict[str, Any]) -> dict[str, Any]:
        fit_score = float(discovery_payload.get("fit_score", 0.0))
        timing_score = float(discovery_payload.get("timing_score", 0.0))

        hypothesis = LeadHypothesisSchema(
            company_name=discovery_payload["company_name"],
            hypothesis_type="managed_services_fit" if fit_score >= 0.75 else "automation_need",
            timing_label="now" if timing_score >= 0.70 else "soon",
            fit_label="high" if fit_score >= 0.80 else "medium",
            actionability_label="high" if discovery_payload.get("signals") else "medium",
            why_now_codes=discovery_payload.get("rationale_codes", []),
            probable_problem_codes=discovery_payload.get("rationale_codes", []),
            recommended_next_action="approve_for_enrichment" if fit_score >= 0.70 else "watchlist",
            confidence=min(float(discovery_payload.get("confidence", 0.0)), 1.0),
        )
        return hypothesis.model_dump(mode="json")

    def _call_backend(self, query: str) -> dict[str, Any]:
        """
        Backend mockeable.
        Si luego conectas Gemini real, sustituye este método.
        """
        use_mock = getattr(settings, "LEAD_RESEARCH_USE_MOCK", True)
        if use_mock:
            return build_mock_payload(query)

        # Punto de integración futuro.
        # Debe devolver dict con:
        # {"query": "...", "items": [...]}
        llm_callable = getattr(settings, "LEAD_RESEARCH_DISCOVERY_BACKEND", None)
        if callable(llm_callable):
            response = llm_callable(query=query)
            return self._coerce_json(response)

        logger.warning("lead_research.discovery.no_backend_configured_falling_back_to_mock query=%s", query)
        return build_mock_payload(query)

    def _is_existing_company(self, company_name: str, normalized_name: str, domain: str) -> bool:
        fields = {f.name for f in Company._meta.get_fields() if hasattr(f, "name")}
        q = Q()

        if "name" in fields:
            q |= Q(name__iexact=company_name)
        if "display_name" in fields:
            q |= Q(display_name__iexact=company_name)
        if "legal_name" in fields:
            q |= Q(legal_name__iexact=company_name)

        if domain:
            if "website" in fields:
                q |= Q(website__icontains=domain)
            if "domain" in fields:
                q |= Q(domain__iexact=domain)

        if not q:
            return False

        return Company.objects.filter(q).exists()

    def _coerce_json(self, raw_payload: str | dict[str, Any]) -> dict[str, Any]:
        if isinstance(raw_payload, dict):
            return raw_payload
        if isinstance(raw_payload, str):
            return json.loads(raw_payload)
        raise TypeError(f"payload type no soportado: {type(raw_payload)!r}")


def normalize_company_name(value: str) -> str:
    value = (value or "").strip().lower()
    for token in [",", ".", " gmbh", " s.l.", " slu", " sl", " ag", " ltd", " llc", " inc"]:
        value = value.replace(token, "")
    return " ".join(value.split())


def extract_domain(url: str) -> str:
    if not url:
        return ""
    parsed = urlparse(url)
    netloc = parsed.netloc or parsed.path
    domain = netloc.lower().strip()
    if domain.startswith("www."):
        domain = domain[4:]
    return domain


def to_decimal(value: float | int | str | Decimal) -> Decimal:
    return Decimal(str(round(float(value), 2)))


def parse_datetime_or_none(value: str | None):
    if not value:
        return None
    try:
        return timezone.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def build_mock_payload(query: str) -> dict[str, Any]:
    """
    Mock estable y estructurado.
    Sustituible por grounding real más adelante.
    """
    if "hiring" in query.lower():
        items = [
            {
                "company_name": "NetForge Systems GmbH",
                "website": "https://www.netforge-systems.de",
                "country": "Germany",
                "city": "Munich",
                "industry": "Industrial Technology",
                "employee_range": "51-200",
                "fit_score": 0.84,
                "timing_score": 0.78,
                "novelty_score": 0.74,
                "confidence": 0.81,
                "rationale_codes": ["dach_presence", "active_hiring", "infra_complexity", "industry_fit"],
                "tags": ["networking", "cloud", "security"],
                "signals": [
                    {
                        "signal_type": "hiring",
                        "signal_value": "network engineer",
                        "confidence": 0.86,
                        "source_ref": "mock://jobs/network-engineer",
                        "observed_at": "2026-03-19T09:00:00Z",
                        "payload": {"department": "infrastructure"},
                    },
                    {
                        "signal_type": "growth",
                        "signal_value": "team expansion",
                        "confidence": 0.75,
                        "source_ref": "mock://growth/team-expansion",
                        "observed_at": "2026-03-19T09:00:00Z",
                        "payload": {},
                    },
                ],
                "metadata": {"seed": "hiring"},
            },
            {
                "company_name": "CloudRail DACH AG",
                "website": "https://www.cloudrail-dach.com",
                "country": "Germany",
                "city": "Frankfurt",
                "industry": "B2B SaaS",
                "employee_range": "201-500",
                "fit_score": 0.80,
                "timing_score": 0.76,
                "novelty_score": 0.71,
                "confidence": 0.79,
                "rationale_codes": ["dach_presence", "mid_market_fit", "active_hiring", "timing_good"],
                "tags": ["saas", "observability", "networking"],
                "signals": [
                    {
                        "signal_type": "hiring",
                        "signal_value": "site reliability engineer",
                        "confidence": 0.81,
                        "source_ref": "mock://jobs/sre",
                        "observed_at": "2026-03-19T10:00:00Z",
                        "payload": {"department": "platform"},
                    }
                ],
                "metadata": {"seed": "hiring"},
            },
        ]
    else:
        items = [
            {
                "company_name": "Auron Gridworks GmbH",
                "website": "https://www.auron-gridworks.de",
                "country": "Germany",
                "city": "Berlin",
                "industry": "Energy Infrastructure",
                "employee_range": "51-200",
                "fit_score": 0.88,
                "timing_score": 0.82,
                "novelty_score": 0.77,
                "confidence": 0.85,
                "rationale_codes": ["dach_presence", "recent_growth", "infra_complexity", "timing_good"],
                "tags": ["energy", "network", "multi-site"],
                "signals": [
                    {
                        "signal_type": "expansion",
                        "signal_value": "new regional sites",
                        "confidence": 0.83,
                        "source_ref": "mock://news/expansion",
                        "observed_at": "2026-03-18T12:00:00Z",
                        "payload": {"region": "DACH"},
                    },
                    {
                        "signal_type": "growth",
                        "signal_value": "operations scaling",
                        "confidence": 0.78,
                        "source_ref": "mock://ops/scaling",
                        "observed_at": "2026-03-18T12:00:00Z",
                        "payload": {},
                    },
                ],
                "metadata": {"seed": "default"},
            },
            {
                "company_name": "Heliox Industrial Cloud GmbH",
                "website": "https://www.heliox-industrial-cloud.de",
                "country": "Germany",
                "city": "Hamburg",
                "industry": "Industrial Software",
                "employee_range": "201-500",
                "fit_score": 0.79,
                "timing_score": 0.74,
                "novelty_score": 0.73,
                "confidence": 0.78,
                "rationale_codes": ["dach_presence", "mid_market_fit", "industry_fit", "recent_growth"],
                "tags": ["industrial", "cloud", "automation"],
                "signals": [
                    {
                        "signal_type": "funding",
                        "signal_value": "growth capital",
                        "confidence": 0.76,
                        "source_ref": "mock://funding/round",
                        "observed_at": "2026-03-17T12:00:00Z",
                        "payload": {"stage": "growth"},
                    }
                ],
                "metadata": {"seed": "default"},
            },
        ]

    return {"query": query, "items": items}
