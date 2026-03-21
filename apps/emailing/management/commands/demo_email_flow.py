# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/emailing/management/commands/demo_email_flow.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
from __future__ import annotations

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.emailing.models import EmailMessage, EmailThread
from services.email_ingest import process_email_message


SCENARIO_BODIES = {
    "interest": "Podríamos valorar una revisión inicial. ¿Qué incluiría exactamente el alcance?",
    "redirect": "No llevo esta parte. No soy la persona adecuada para esto.",
    "timing": "Ahora no, escríbeme en mayo y lo retomamos.",
    "budget": "Antes de avanzar necesitaríamos entender mejor el presupuesto y el precio.",
    "light": "Gracias.",
}


class Command(BaseCommand):
    help = "Ejecuta el pipeline demo de email de extremo a extremo."

    def add_arguments(self, parser):
        parser.add_argument(
            "--scenario",
            default="interest",
            choices=["interest", "redirect", "timing", "budget", "light"],
        )

    def handle(self, *args, **options):
        scenario = options["scenario"]
        body_text = SCENARIO_BODIES[scenario]

        thread = EmailThread.objects.create(
            subject=f"Demo scenario: {scenario}",
            external_provider="demo",
            thread_status="open",
        )

        email_message = EmailMessage.objects.create(
            thread=thread,
            external_message_ref=f"demo-{scenario}-{timezone.now().timestamp()}",
            direction="inbound",
            sender="demo@example.com",
            subject=f"Demo scenario: {scenario}",
            body_text=body_text,
            sent_at=timezone.now(),
            message_status="synced",
        )

        result = process_email_message(email_message)

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=== DEMO EMAIL FLOW OK ==="))
        self.stdout.write(f"Scenario: {scenario}")
        self.stdout.write(f"Thread ID: {thread.pk}")
        self.stdout.write(f"Email ID: {email_message.pk}")
        self.stdout.write(f"Facts created: {len(result['facts'])}")
        self.stdout.write(f"Inferences created: {len(result['inferences'])}")
        self.stdout.write(f"Proposals created: {len(result['proposals'])}")
        self.stdout.write(f"Recommendations created: {len(result.get('recommendations', []))}")

        if result["facts"]:
            self.stdout.write("")
            self.stdout.write("--- Facts ---")
            for fact in result["facts"]:
                self.stdout.write(
                    f"[{fact.pk}] {fact.fact_type} | confidence={fact.confidence} | value={fact.fact_value}"
                )

        if result["inferences"]:
            self.stdout.write("")
            self.stdout.write("--- Inferences ---")
            for inf in result["inferences"]:
                self.stdout.write(
                    f"[{inf.pk}] {inf.inference_type} | confidence={inf.confidence} | value={inf.inference_value}"
                )

        if result["proposals"]:
            self.stdout.write("")
            self.stdout.write("--- Proposals ---")
            for prop in result["proposals"]:
                self.stdout.write(
                    f"[{prop.pk}] {prop.proposed_change_type} | status={prop.proposal_status} | confidence={prop.confidence}"
                )

        if result["recommendations"]:
            self.stdout.write("")
            self.stdout.write("--- Recommendations ---")
            for rec in result["recommendations"]:
                rec_type = getattr(rec, "recommendation_type", "-")
                rec_text = getattr(rec, "recommendation_text", "-")
                rec_confidence = getattr(rec, "confidence", "-")
                rec_status = getattr(rec, "status", "-")
                self.stdout.write(
                    f"[{rec.pk}] {rec_type} | status={rec_status} | confidence={rec_confidence} | text={rec_text}"
                )
