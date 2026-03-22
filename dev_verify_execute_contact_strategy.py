# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/dev_verify_execute_contact_strategy.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
from django.test import RequestFactory

from apps.recommendations.models import AIRecommendation
from apps.emailing.models import OutboundEmail
from apps.recommendations.views import execute_contact_strategy

rf = RequestFactory()

print("=== PRECHECK ===")
candidates = list(
    AIRecommendation.objects.filter(
        status=AIRecommendation.STATUS_NEW,
        recommendation_type="contact_strategy",
        scope_type="opportunity",
    ).order_by("-id")[:10]
)

if not candidates:
    print("No hay recommendations contact_strategy/new/scope=opportunity")
    for rec in AIRecommendation.objects.order_by("-id")[:10]:
        print({
            "id": rec.id,
            "type": rec.recommendation_type,
            "status": rec.status,
            "scope_type": rec.scope_type,
            "scope_id": rec.scope_id,
        })
    raise SystemExit(0)

rec = candidates[0]
print("Recommendation elegida:", {
    "id": rec.id,
    "type": rec.recommendation_type,
    "status": rec.status,
    "scope_type": rec.scope_type,
    "scope_id": rec.scope_id,
})

before_total = OutboundEmail.objects.count()
before_first_contact = OutboundEmail.objects.filter(
    opportunity_id=int(rec.scope_id),
    email_type=OutboundEmail.TYPE_FIRST_CONTACT,
).count()

print("Outbound total before:", before_total)
print("First contact for opportunity before:", before_first_contact)

print("\n=== FIRST EXECUTION ===")
request_1 = rf.post(f"/recommendations/{rec.id}/execute-contact-strategy/")
response_1 = execute_contact_strategy(request_1, rec.id)
print("Response 1 status:", response_1.status_code)
print("Response 1 location:", response_1["Location"])

rec.refresh_from_db()
after_first_total = OutboundEmail.objects.count()
after_first_contact = OutboundEmail.objects.filter(
    opportunity_id=int(rec.scope_id),
    email_type=OutboundEmail.TYPE_FIRST_CONTACT,
).count()

print("Recommendation status after first:", rec.status)
print("Outbound total after first:", after_first_total)
print("First contact for opportunity after first:", after_first_contact)

print("\n=== SECOND EXECUTION ===")
request_2 = rf.post(f"/recommendations/{rec.id}/execute-contact-strategy/")
response_2 = execute_contact_strategy(request_2, rec.id)
print("Response 2 status:", response_2.status_code)
print("Response 2 location:", response_2["Location"])

rec.refresh_from_db()
after_second_total = OutboundEmail.objects.count()
after_second_contact = OutboundEmail.objects.filter(
    opportunity_id=int(rec.scope_id),
    email_type=OutboundEmail.TYPE_FIRST_CONTACT,
).count()

print("Recommendation status after second:", rec.status)
print("Outbound total after second:", after_second_total)
print("First contact for opportunity after second:", after_second_contact)

print("\n=== RESULT ===")
print({
    "created_on_first_run": after_first_total - before_total,
    "created_on_second_run": after_second_total - after_first_total,
    "first_contact_delta_first_run": after_first_contact - before_first_contact,
    "first_contact_delta_second_run": after_second_contact - after_first_contact,
    "final_status": rec.status,
})
