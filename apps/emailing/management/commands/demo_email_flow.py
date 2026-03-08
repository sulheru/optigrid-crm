from __future__ import annotations

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.emailing.models import EmailThread, EmailMessage
from apps.events.models import Event
from apps.facts.models import FactRecord
from apps.inferences.models import InferenceRecord
from apps.updates.models import CRMUpdateProposal
from services.events import record_event
from services.email_ingest import process_email_message


def _model_field_names(model) -> set[str]:
    return {f.name for f in model._meta.get_fields() if getattr(f, "concrete", False)}


def _filtered_kwargs(model, raw: dict) -> dict:
    allowed = _model_field_names(model)
    return {k: v for k, v in raw.items() if k in allowed}


class Command(BaseCommand):
    help = "Crea un EmailThread + EmailMessage de demo y ejecuta el pipeline completo."

    def add_arguments(self, parser):
        parser.add_argument(
            "--scenario",
            type=str,
            default="interest",
            choices=["interest", "redirect", "timing", "budget", "light"],
            help="Escenario de email a simular.",
        )

    def _scenario_payload(self, scenario: str) -> tuple[str, str]:
        if scenario == "redirect":
            return (
                "Redirección de interlocutor",
                "No llevo esta parte. No soy la persona adecuada. "
                "Puedes escribir a otra persona del equipo.",
            )
        if scenario == "timing":
            return (
                "Retomar más adelante",
                "Ahora mismo no. Escríbeme en mayo y lo retomamos.",
            )
        if scenario == "budget":
            return (
                "Consulta sobre coste",
                "Nos interesa entender el alcance, pero antes necesito una idea del precio y del presupuesto.",
            )
        if scenario == "light":
            return (
                "Respuesta breve",
                "Gracias, suena interesante.",
            )

        return (
            "Interés inicial",
            "Podríamos valorar una revisión inicial. ¿Qué incluiría exactamente el alcance?",
        )

    def handle(self, *args, **options):
        scenario = options["scenario"]
        subject, body = self._scenario_payload(scenario)
        now = timezone.now()

        thread_kwargs = {
            "external_provider": "m365",
            "external_thread_ref": f"demo-thread-{scenario}-{now.timestamp()}",
            "subject": subject,
            "thread_status": "open",
            "first_message_at": now,
            "last_message_at": now,
        }
        thread = EmailThread.objects.create(**_filtered_kwargs(EmailThread, thread_kwargs))

        record_event(
            event_type="email_thread_linked",
            aggregate_type="email_thread",
            aggregate_id=thread.id,
            payload={"external_thread_ref": getattr(thread, "external_thread_ref", "")},
            triggered_by_type="system",
        )

        email_kwargs = {
            "thread": thread,
            "external_message_ref": f"demo-message-{scenario}-{now.timestamp()}",
            "direction": "inbound",
            "sender": "demo@example.com",
            "recipients": ["hans@example.com"],
            "cc": [],
            "subject": subject,
            "body_text": body,
            "body_html": "",
            "sent_at": now,
            "received_at": now,
            "message_status": "synced",
        }
        email = EmailMessage.objects.create(**_filtered_kwargs(EmailMessage, email_kwargs))

        record_event(
            event_type="email_message_synced",
            aggregate_type="email_message",
            aggregate_id=email.id,
            payload={
                "direction": getattr(email, "direction", ""),
                "subject": getattr(email, "subject", ""),
            },
            triggered_by_type="external_provider",
            triggered_by_id="demo_m365",
        )

        record_event(
            event_type="email_received",
            aggregate_type="email_message",
            aggregate_id=email.id,
            payload={"sender": getattr(email, "sender", "")},
            triggered_by_type="external_provider",
            triggered_by_id="demo_m365",
        )

        result = process_email_message(email)

        facts = FactRecord.objects.filter(
            source_type="email_message",
            source_id=email.id,
        ).order_by("id")

        inferences = InferenceRecord.objects.filter(
            source_type="fact_record",
            source_id__in=facts.values_list("id", flat=True),
        ).order_by("id")

        inference_ids = list(inferences.values_list("id", flat=True))

        proposals = CRMUpdateProposal.objects.none()
        if inference_ids:
            proposals = CRMUpdateProposal.objects.filter(
                proposed_payload__source_inference_id__in=inference_ids
            ).order_by("id")

        events = Event.objects.order_by("-id")[:20]

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=== DEMO EMAIL FLOW OK ==="))
        self.stdout.write(f"Scenario: {scenario}")
        self.stdout.write(f"Thread ID: {thread.id}")
        self.stdout.write(f"Email ID: {email.id}")
        self.stdout.write(f"Facts created: {result.facts_created}")
        self.stdout.write(f"Inferences created: {result.inferences_created}")
        self.stdout.write(f"Proposals created: {result.proposals_created}")

        self.stdout.write("\n--- Facts ---")
        for fact in facts:
            self.stdout.write(
                f"[{fact.id}] {fact.fact_type} | confidence={fact.confidence} | value={fact.fact_value}"
            )

        self.stdout.write("\n--- Inferences ---")
        for inf in inferences:
            self.stdout.write(
                f"[{inf.id}] {inf.inference_type} | confidence={inf.confidence} | value={inf.inference_value}"
            )

        self.stdout.write("\n--- CRM Update Proposals ---")
        for proposal in proposals:
            self.stdout.write(
                f"[{proposal.id}] {proposal.proposed_change_type} | "
                f"status={proposal.proposal_status} | approval_required={proposal.approval_required}"
            )

        self.stdout.write("\n--- Recent Events ---")
        for event in events:
            self.stdout.write(
                f"[{event.id}] {event.event_type} -> {event.aggregate_type}:{event.aggregate_id}"
            )
