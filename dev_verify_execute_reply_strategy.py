from django.test import RequestFactory

from apps.recommendations.models import AIRecommendation
from apps.emailing.models import InboundEmail, OutboundEmail
from apps.recommendations.views import execute_reply_strategy

rf = RequestFactory()

print("=== PRECHECK ===")
candidates = list(
    AIRecommendation.objects.filter(
        status=AIRecommendation.STATUS_NEW,
        recommendation_type="reply_strategy",
        scope_type="opportunity",
    ).order_by("-id")[:10]
)

if not candidates:
    print("No hay recommendations reply_strategy/new/scope=opportunity")
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

opportunity_id = int(rec.scope_id)
latest_inbound = (
    InboundEmail.objects.filter(opportunity_id=opportunity_id)
    .order_by("-received_at", "-created_at")
    .first()
)

print("Latest inbound:", {
    "id": getattr(latest_inbound, "id", None),
    "opportunity_id": getattr(latest_inbound, "opportunity_id", None),
})

before_total = OutboundEmail.objects.count()
before_followup = 0
if latest_inbound is not None:
    before_followup = OutboundEmail.objects.filter(
        source_inbound=latest_inbound,
        email_type=OutboundEmail.TYPE_FOLLOWUP,
    ).count()

print("Outbound total before:", before_total)
print("Followups for latest inbound before:", before_followup)

print("\n=== FIRST EXECUTION ===")
request_1 = rf.post(f"/recommendations/{rec.id}/execute-reply-strategy/")
response_1 = execute_reply_strategy(request_1, rec.id)
print("Response 1 status:", response_1.status_code)
print("Response 1 location:", response_1["Location"])

rec.refresh_from_db()
after_first_total = OutboundEmail.objects.count()
after_first_followup = 0
if latest_inbound is not None:
    after_first_followup = OutboundEmail.objects.filter(
        source_inbound=latest_inbound,
        email_type=OutboundEmail.TYPE_FOLLOWUP,
    ).count()

print("Recommendation status after first:", rec.status)
print("Outbound total after first:", after_first_total)
print("Followups for latest inbound after first:", after_first_followup)

print("\n=== SECOND EXECUTION ===")
request_2 = rf.post(f"/recommendations/{rec.id}/execute-reply-strategy/")
response_2 = execute_reply_strategy(request_2, rec.id)
print("Response 2 status:", response_2.status_code)
print("Response 2 location:", response_2["Location"])

rec.refresh_from_db()
after_second_total = OutboundEmail.objects.count()
after_second_followup = 0
if latest_inbound is not None:
    after_second_followup = OutboundEmail.objects.filter(
        source_inbound=latest_inbound,
        email_type=OutboundEmail.TYPE_FOLLOWUP,
    ).count()

print("Recommendation status after second:", rec.status)
print("Outbound total after second:", after_second_total)
print("Followups for latest inbound after second:", after_second_followup)

print("\n=== RESULT ===")
print({
    "created_on_first_run": after_first_total - before_total,
    "created_on_second_run": after_second_total - after_first_total,
    "followup_delta_first_run": after_first_followup - before_followup,
    "followup_delta_second_run": after_second_followup - after_first_followup,
    "final_status": rec.status,
})
