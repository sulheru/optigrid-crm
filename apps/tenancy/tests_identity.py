from django.test import TestCase

from apps.tenancy.models import (
    CorporateDomain,
    CorporateMembership,
    Identity,
    MailboxAccount,
    OperatingOrganization,
)
from apps.tenancy.services.domain_resolution import (
    extract_domain_from_email,
    resolve_operating_organization_from_domain,
    resolve_operating_organization_from_email,
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
        self.mailbox = MailboxAccount.objects.create(
            operating_organization=self.org,
            display_name="Sales",
            email="sales@optigrid.com",
            account_key="sales-main",
            provider="mail_stub",
            is_primary=True,
            status=MailboxAccount.Status.ACTIVE,
        )

    def test_extract_domain_from_email(self):
        self.assertEqual(
            extract_domain_from_email("Hans@OptiGrid.com"),
            "optigrid.com",
        )

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
