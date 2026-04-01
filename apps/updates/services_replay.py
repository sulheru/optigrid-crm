from apps.emailing.models import InboundEmail

from .services import create_basic_proposal
from .services_diff import diff_proposals


def replay_email(email_id: int, simulate: bool = True):
    email = InboundEmail.objects.get(id=email_id)

    return create_basic_proposal(
        email=email,
        simulate=simulate,
    )


def replay_with_diff(email_id: int):
    email = InboundEmail.objects.get(id=email_id)

    old = create_basic_proposal(email, simulate=True)
    new = create_basic_proposal(email, simulate=True)

    return {
        "old": old,
        "new": new,
        "diff": diff_proposals(old, new),
    }


def replay_with_version(email_id: int, version: str):
    email = InboundEmail.objects.get(id=email_id)

    old = create_basic_proposal(email, simulate=True)
    new = create_basic_proposal(email, simulate=True, rules_version=version)

    return {
        "version": version,
        "old": old,
        "new": new,
        "diff": diff_proposals(old, new),
    }
