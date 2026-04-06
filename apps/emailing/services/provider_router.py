from apps.emailing.smll_adapter import inbound_to_smll, smll_to_outbound
from apps.emailing.services.smll_bootstrap import ensure_generic_persona
from apps.simulated_personas.runtime.smll_engine import build_simulated_reply
from apps.tenancy.services.eil_context import ensure_email_eil_context
from services.email_ingest import process_email_message


def process_email_with_provider(email, *, mailbox_account):
    context = ensure_email_eil_context(
        email,
        mailbox_account=mailbox_account,
        require_mailbox=True,
        require_address=True,
        persist=True,
    )

    mailbox = context["mailbox_account"]

    # 🔥 GARANTIZAR PERSONA
    ensure_generic_persona(mailbox)

    smll_input = inbound_to_smll(email, mailbox_account=mailbox)

    result = build_simulated_reply(
        operating_organization=context["operating_organization"],
        incoming_message=smll_input,
        mailbox_account=mailbox,
    )

    return smll_to_outbound(email, result)


def route_inbound_email(email):
    return process_email_message(email)
