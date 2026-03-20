# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/emailing/services/outbound_sender.py
from django.utils import timezone

from apps.emailing.models import OutboundEmail
from apps.emailing.services.inbound_simulator import simulate_inbound_reply_for_outbound


def send_outbound_email(email: OutboundEmail) -> dict:
    if email.status not in [OutboundEmail.STATUS_APPROVED]:
        return {
            "ok": False,
            "reason": f"invalid_status:{email.status}",
        }

    print(
        f"SENDING EMAIL -> id={email.id} "
        f"type={email.email_type} "
        f"subject={email.subject}"
    )

    email.status = OutboundEmail.STATUS_SENT
    email.sent_at = timezone.now()
    email.failed_at = None
    email.failure_reason = ""
    email.save(update_fields=["status", "sent_at", "failed_at", "failure_reason", "updated_at"])

    inbound = simulate_inbound_reply_for_outbound(email)

    return {
        "ok": True,
        "email_id": email.id,
        "status": email.status,
        "inbound_email_id": inbound.id,
    }


def send_all_approved_outbound_emails(email_type: str | None = None) -> dict:
    emails = OutboundEmail.objects.filter(status=OutboundEmail.STATUS_APPROVED)

    if email_type:
        emails = emails.filter(email_type=email_type)

    emails = emails.order_by("created_at")

    sent = 0
    failed = 0

    for email in emails:
        result = send_outbound_email(email)
        if result["ok"]:
            sent += 1
        else:
            failed += 1

    return {
        "sent": sent,
        "failed": failed,
    }
