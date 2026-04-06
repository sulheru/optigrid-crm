from __future__ import annotations

from apps.tenancy.models import OperatingOrganization, MailboxAccount


def get_or_create_default_organization():
    org, _ = OperatingOrganization.objects.get_or_create(
        name="SMLL Sandbox Org"
    )
    return org


def get_or_create_default_mailbox():
    org = get_or_create_default_organization()

    mailbox = MailboxAccount.objects.filter(
        operating_organization=org
    ).first()

    if mailbox:
        return mailbox

    return MailboxAccount.objects.create(
        email="sandbox@smll.local",
        is_active=True,
        operating_organization=org,
    )
