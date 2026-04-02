from django.urls import path

from .views import (
    approve_email,
    apply_decision,
    back_to_draft,
    bulk_action,
    dismiss_decision,
    generate_reply_draft,
    inbox_view,
    mark_inbound_linked,
    mark_inbound_reviewed,
    outbox_view,
    send_all,
    send_email,
    update_outbound_email,
)
from .views_decision import email_decision_detail

urlpatterns = [
    path("outbox/", outbox_view, name="outbox"),
    path("outbox/<int:pk>/approve/", approve_email, name="approve_email"),
    path("outbox/<int:pk>/draft/", back_to_draft, name="back_to_draft"),
    path("outbox/<int:pk>/send/", send_email, name="send_email"),
    path("outbox/<int:pk>/update/", update_outbound_email, name="update_outbound_email"),
    path("outbox/send/", send_all, name="send_all_emails"),
    path("outbox/bulk-action/", bulk_action, name="bulk_outbox_action"),

    path("inbox/", inbox_view, name="inbox"),
    path("inbox/<int:pk>/reviewed/", mark_inbound_reviewed, name="mark_inbound_reviewed"),
    path("inbox/<int:pk>/linked/", mark_inbound_linked, name="mark_inbound_linked"),
    path("inbox/<int:pk>/generate-reply/", generate_reply_draft, name="generate_reply_draft"),
    path("inbox/<int:pk>/apply-decision/", apply_decision, name="apply_decision"),
    path("inbox/<int:pk>/dismiss-decision/", dismiss_decision, name="dismiss_decision"),
    path("inbox/<int:email_id>/decision/", email_decision_detail, name="email_decision_detail"),
]
