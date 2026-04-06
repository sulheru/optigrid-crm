from apps.emailing.services.smll_bootstrap import get_default_mailbox
from apps.emailing.services.provider_router import process_email_with_provider


def process_incoming_email(email):
    # 🔥 aquí sí tiene sentido (capa aplicación)
    if email.mailbox_account_id is None:
        email.mailbox_account = get_default_mailbox()
        email.save()

    return process_email_with_provider(
        email,
        mailbox_account=email.mailbox_account,
    )
