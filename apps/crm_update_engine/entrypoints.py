from __future__ import annotations

from apps.facts.services import create_email_fact
from apps.inferences.services import create_basic_email_inference
from apps.recommendations.services_engine import create_basic_email_recommendation
from apps.tenancy.services.eil_context import ensure_email_eil_context
from apps.updates.services import create_basic_proposal


def process_email(email):
    ensure_email_eil_context(
        email,
        require_mailbox=False,
        require_address=True,
        persist=True,
    )

    create_email_fact(email)
    create_basic_email_inference(email)
    create_basic_proposal(email)
    create_basic_email_recommendation(email)
