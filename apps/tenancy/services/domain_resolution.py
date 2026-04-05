from __future__ import annotations

from django.db import transaction
from django.utils.text import slugify

from apps.tenancy.models import (
    CorporateDomain,
    EmailIdentity,
    OperatingOrganization,
    PublicEmailDomain,
    extract_domain,
    normalize_domain,
    normalize_email,
)


def extract_domain_from_email(email: str) -> str:
    return extract_domain(email)


def is_public_email_domain(domain: str) -> bool:
    domain = normalize_domain(domain)
    if not domain:
        return False
    return PublicEmailDomain.objects.filter(domain=domain, is_active=True).exists()


def resolve_operating_organization_from_domain(domain: str) -> OperatingOrganization | None:
    domain = normalize_domain(domain)
    if not domain:
        return None

    corporate = (
        CorporateDomain.objects.select_related("operating_organization")
        .filter(domain=domain, is_active=True)
        .first()
    )
    if corporate is not None:
        return corporate.operating_organization

    return (
        OperatingOrganization.objects.filter(primary_domain=domain)
        .order_by("id")
        .first()
    )


@transaction.atomic
def create_provisional_organization(domain: str) -> OperatingOrganization:
    domain = normalize_domain(domain)
    if not domain:
        raise ValueError("create_provisional_organization requires a valid domain.")

    existing = resolve_operating_organization_from_domain(domain)
    if existing is not None:
        return existing

    base_slug = slugify(domain.replace(".", "-")) or "organization"
    slug = f"prov-{base_slug}"[:120]
    idx = 2
    while OperatingOrganization.objects.filter(slug=slug).exists():
        suffix = f"-{idx}"
        root = f"prov-{base_slug}"
        slug = f"{root[:120-len(suffix)]}{suffix}"
        idx += 1

    org = OperatingOrganization.objects.create(
        name=f"Provisional {domain}",
        slug=slug,
        legal_name=f"Provisional {domain}",
        primary_domain=domain,
        is_simulated=domain.endswith(".sim"),
        status=OperatingOrganization.Status.PROVISIONAL,
        notes="Created automatically by EIL resolution.",
    )

    CorporateDomain.objects.create(
        operating_organization=org,
        domain=domain,
        is_primary=True,
        is_active=True,
        notes="Auto-created by EIL resolution.",
    )

    return org


@transaction.atomic
def resolve_email_identity(email: str) -> EmailIdentity:
    normalized_email = normalize_email(email)
    domain = extract_domain_from_email(normalized_email)

    if not normalized_email or not domain:
        raise ValueError("resolve_email_identity requires a valid email address.")

    existing = (
        EmailIdentity.objects.select_related("operating_organization")
        .filter(email=normalized_email)
        .first()
    )
    if existing is not None:
        return existing

    org = resolve_operating_organization_from_domain(domain)
    if org is None:
        org = create_provisional_organization(domain)

    return EmailIdentity.objects.create(
        operating_organization=org,
        email=normalized_email,
        display_name="",
        account_key=normalized_email,
        provider="system",
        is_primary=False,
        status=EmailIdentity.Status.ACTIVE,
    )


@transaction.atomic
def resolve_organization(email_identity: EmailIdentity) -> OperatingOrganization:
    if email_identity.operating_organization_id:
        return email_identity.operating_organization

    domain = extract_domain_from_email(email_identity.email)
    org = resolve_operating_organization_from_domain(domain)
    if org is None:
        org = create_provisional_organization(domain)

    email_identity.operating_organization = org
    email_identity.save(update_fields=["operating_organization", "updated_at"])
    return org


def resolve_operating_organization_from_email(email: str) -> OperatingOrganization | None:
    domain = extract_domain_from_email(email)
    if not domain:
        return None
    return resolve_operating_organization_from_domain(domain)
