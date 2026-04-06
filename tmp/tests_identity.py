from django.test import TestCase

from apps.tenancy.models import (
    CorporateDomain,
    CorporateMembership,
    EmailIdentity,
    Identity,
    MailboxAccount,
    OperatingOrganization,
    PublicEmailDomain,
)
from apps.tenancy.services.domain_resolution import (
    create_provisional_organization,
    extract_domain_from_email,
    is_public_email_domain,
    resolve_email_identity,
    resolve_operating_organization_from_domain,
    resolve_operating_organization_from_email,
    resolve_organization,
)


class TenancyIdentityLayerTests(TestCase):
    def setUp(self):
        self.org = OperatingOrganization.objects.create(
            name="OptiGrid GmbH",
            slug="optigrid-gmbh",
            legal_name="OptiGrid GmbH",
            primary_domain="optigrid.com",
            is_simulated=False,
            status=OperatingOrganization.Status.ACTIVE,
        )
        self.domain = CorporateDomain.objects.create(
            operating_organization=self.org,
            domain="optigrid.com",
            is_primary=True,
            is_active=True,
        )

        PublicEmailDomain.objects.get_or_create(
            domain="gmail.com",
            defaults={
                "is_active": True,
                "notes": "Test fixture",
            },
        )

        self.mailbox = MailboxAccount.objects.create(
            operating_organization=self.org,
            display_name="Sales",
            email="sales@optigrid.com",
            account_key="sales-main",
            provider="mail_stub",
            is_primary=True,
            status=MailboxAccount.Status.ACTIVE,
            metadata={},
        )

    def test_extract_domain_from_email(self):
        self.assertEqual(extract_domain_from_email("Hans@OptiGrid.com"), "optigrid.com")

    def test_is_public_email_domain(self):
        self.assertTrue(is_public_email_domain("gmail.com"))
        self.assertFalse(is_public_email_domain("optigrid.com"))

    def test_resolve_operating_organization_from_domain(self):
        resolved = resolve_operating_organization_from_domain("optigrid.com")
        self.assertEqual(resolved, self.org)

    def test_resolve_operating_organization_from_email(self):
        resolved = resolve_operating_organization_from_email("alex@optigrid.com")
        self.assertEqual(resolved, self.org)

    def test_resolve_falls_back_to_primary_domain(self):
        CorporateDomain.objects.filter(pk=self.domain.pk).delete()
        resolved = resolve_operating_organization_from_email("ops@optigrid.com")
        self.assertEqual(resolved, self.org)

    def test_mailbox_corporation_alias_points_to_operating_organization(self):
        self.assertEqual(self.mailbox.corporation, self.org)

    def test_membership_links_identity_to_operating_organization(self):
        identity = Identity.objects.create(
            email="user@optigrid.com",
            display_name="Hans",
            status=Identity.Status.ACTIVE,
        )
        membership = CorporateMembership.objects.create(
            identity=identity,
            operating_organization=self.org,
            role=CorporateMembership.Role.ADMIN,
            status=CorporateMembership.Status.ACTIVE,
            is_default=True,
        )
        self.assertEqual(membership.operating_organization, self.org)
        self.assertEqual(membership.identity, identity)

    def test_resolve_email_identity_creates_new_eil_identity(self):
        identity = resolve_email_identity("hello@optigrid.com")
        self.assertEqual(identity.email, "hello@optigrid.com")
        self.assertEqual(identity.operating_organization, self.org)
        self.assertFalse(identity.is_public_domain)

    def test_resolve_email_identity_creates_provisional_org_for_unknown_domain(self):
        identity = resolve_email_identity("hello@example.org")
        self.assertEqual(identity.email, "hello@example.org")
        self.assertEqual(identity.operating_organization.primary_domain, "example.org")
        self.assertEqual(
            identity.operating_organization.status,
            OperatingOrganization.Status.PROVISIONAL,
        )

    def test_create_provisional_organization(self):
        org = create_provisional_organization("empresa.com.sim")
        self.assertEqual(org.primary_domain, "empresa.com.sim")
        self.assertTrue(org.is_simulated)
        self.assertEqual(org.status, OperatingOrganization.Status.PROVISIONAL)

    def test_resolve_organization_returns_identity_org(self):
        identity = resolve_email_identity("sales-ops@optigrid.com")
        self.assertEqual(resolve_organization(identity), self.org)
