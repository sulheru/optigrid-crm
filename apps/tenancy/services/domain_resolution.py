from __future__ import annotations

from apps.tenancy.models import CorporateDomain, OperatingOrganization


def normalize_domain(value: str) -> str:
    return (value or "").strip().lower()


def extract_domain_from_email(email: str) -> str:
    email = (email or "").strip().lower()
    if "@" not in email:
        return ""
    return email.split("@", 1)[1].strip().lower()


def resolve_operating_organization_from_domain(domain: str) -> OperatingOrganization | None:
    domain = normalize_domain(domain)
    if not domain:
        return None

    corporate_domain = (
        CorporateDomain.objects.select_related("operating_organization")
        .filter(domain=domain, is_active=True)
        .first()
    )
    if corporate_domain is not None:
        return corporate_domain.operating_organization

    fallback = (
        OperatingOrganization.objects.filter(
            primary_domain=domain,
            status=OperatingOrganization.Status.ACTIVE,
        )
        .order_by("id")
        .first()
    )
    return fallback


def resolve_operating_organization_from_email(email: str) -> OperatingOrganization | None:
    domain = extract_domain_from_email(email)
    if not domain:
        return None
    return resolve_operating_organization_from_domain(domain)
