# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/dev_verify_execute_unified.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
from django.test import RequestFactory

from apps.recommendations.models import AIRecommendation
from apps.emailing.models import OutboundEmail
from apps.recommendations.views import execute_recommendation

rf = RequestFactory()

print("=== PRECHECK ===")
candidates = list(
    AIRecommendation.objects.filter(
        status=AIRecommendation.STATUS_NEW,
        recommendation_type__in=["followup", "contact_strategy", "reply_strategy"],
        scope_type="opportunity",
    ).order_by("-id")[:20]
)

if not candidates:
    print("No hay recommendations ejecutables en estado new")
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

print("Outbound total before:", before_total)

print("\n=== FIRST EXECUTION ===")
request_1 = rf.post(f"/recommendations/{rec.id}/execute/")
response_1 = execute_recommendation(request_1, rec.id)
print("Response 1 status:", response_1.status_code)
print("Response 1 location:", response_1["Location"])

rec.refresh_from_db()
after_first_total = OutboundEmail.objects.count()

print("Recommendation status after first:", rec.status)
print("Outbound total after first:", after_first_total)

print("\n=== SECOND EXECUTION ===")
request_2 = rf.post(f"/recommendations/{rec.id}/execute/")
response_2 = execute_recommendation(request_2, rec.id)
print("Response 2 status:", response_2.status_code)
print("Response 2 location:", response_2["Location"])

rec.refresh_from_db()
after_second_total = OutboundEmail.objects.count()

print("Recommendation status after second:", rec.status)
print("Outbound total after second:", after_second_total)

print("\n=== RESULT ===")
print({
    "recommendation_type": rec.recommendation_type,
    "created_on_first_run": after_first_total - before_total,
    "created_on_second_run": after_second_total - after_first_total,
    "final_status": rec.status,
})
