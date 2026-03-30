from django.db import models


def patch_emailmessage_model(EmailMessage):
    """
    Patch dinámico para evitar tocar migrations ahora mismo.
    (Se puede formalizar en migration después)
    """

    if not hasattr(EmailMessage, "is_simulated"):
        EmailMessage.add_to_class(
            "is_simulated",
            models.BooleanField(default=False),
        )

    if not hasattr(EmailMessage, "source"):
        EmailMessage.add_to_class(
            "source",
            models.CharField(max_length=32, null=True, blank=True),
        )

    return EmailMessage
