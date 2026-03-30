from apps.emailing.services.smll_bootstrap import create_simulated_inbound_email
from apps.emailing.services.email_processing_patch import process_incoming_email
from django.apps import apps

InboundEmail = apps.get_model("emailing", "InboundEmail")
OutboundEmail = apps.get_model("emailing", "OutboundEmail")
Opportunity = apps.get_model("opportunities", "Opportunity")

# Estado inicial
before_inbound = InboundEmail.objects.count()
before_outbound = OutboundEmail.objects.count()
before_opps = Opportunity.objects.count()

# Crear inbound simulado
email = create_simulated_inbound_email(
    subject="Test SMLL",
    body="We are exploring improvements in our IT setup and would like to understand your approach.",
    from_email="test@company.com",
)

# Procesar pipeline (incluye SMLL)
process_incoming_email(email)

# Estado final
after_inbound = InboundEmail.objects.count()
after_outbound = OutboundEmail.objects.count()
after_opps = Opportunity.objects.count()

print("Inbound:", before_inbound, "->", after_inbound)
print("Outbound:", before_outbound, "->", after_outbound)
print("Opportunity:", before_opps, "->", after_opps)

# Últimos registros
last_inbound = InboundEmail.objects.order_by("-id").first()
last_outbound = OutboundEmail.objects.order_by("-id").first()
last_opp = Opportunity.objects.order_by("-id").first()

print("\n--- LAST OPPORTUNITY ---")
print(last_opp.id, last_opp.title, last_opp.company_name, last_opp.stage)

print("\n--- LAST INBOUND ---")
print(last_inbound.id, last_inbound.from_email, last_inbound.subject, last_inbound.opportunity_id)

print("\n--- LAST OUTBOUND ---")
print(last_outbound.id, last_outbound.to_email, last_outbound.subject, last_outbound.opportunity_id)
print(last_outbound.body[:500])
