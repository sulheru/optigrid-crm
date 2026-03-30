from apps.emailing.smll_adapter import inbound_to_smll, smll_to_outbound
from apps.simulated_personas.runtime.smll_engine import build_simulated_reply


def process_email_with_provider(email, *, mailbox_account):
    if mailbox_account is None:
        raise ValueError(
            "SMLL requiere mailbox_account explícito. "
            "InboundEmail/Opportunity no contienen contexto de tenant/mailbox."
        )

    smll_input = inbound_to_smll(email, mailbox_account=mailbox_account)

    result = build_simulated_reply(
        operating_organization=mailbox_account.operating_organization,
        incoming_message=smll_input,
        mailbox_account=mailbox_account,
    )

    return smll_to_outbound(email, result)
