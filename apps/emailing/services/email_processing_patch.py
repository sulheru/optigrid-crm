from apps.emailing.services.provider_router import process_email_with_provider


def process_incoming_email(email, *, mailbox_account=None, use_provider=True):
    reply = None

    if use_provider:
        reply = process_email_with_provider(
            email,
            mailbox_account=mailbox_account,
        )

        if reply is not None:
            _continue_pipeline(reply)

    _continue_pipeline(email)
    return reply


def _continue_pipeline(email):
    try:
        from apps.crm_update_engine.entrypoints import process_email
        process_email(email)
    except ModuleNotFoundError:
        print("[SMLL] CRM Update Engine no disponible, pipeline detenido aquí")
