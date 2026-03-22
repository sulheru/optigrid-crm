from django.test import RequestFactory

from apps.recommendations.models import AIRecommendation
from apps.emailing.models import OutboundEmail
from apps.recommendations.views import execute_followup

rf = RequestFactory()

print("=== PRECHECK ===")
candidates = list(
    AIRecommendation.objects.filter(
        status=AIRecommendation.STATUS_NEW,
        recommendation_type="followup",
        scope_type="opportunity",
    ).order_by("-id")[:10]
)

if not candidates:
    print("No hay recommendations followup/new/scope=opportunity")
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
before_linked = list(
    OutboundEmail.objects.filter(source_recommendation=rec)
    .order_by("-created_at")
    .values(
        "id",
        "email_type",
        "status",
        "opportunity_id",
        "source_inbound_id",
        "source_recommendation_id",
        "created_at",
    )
)

print("Outbound total before:", before_total)
print("Linked to rec before:", len(before_linked))
for row in before_linked:
    print(row)

print("\n=== FIRST EXECUTION ===")
request_1 = rf.post(f"/recommendations/{rec.id}/execute-followup/")
response_1 = execute_followup(request_1, rec.id)
print("Response 1 status:", response_1.status_code)
print("Response 1 location:", response_1["Location"])

rec.refresh_from_db()

after_first_total = OutboundEmail.objects.count()
linked_after_first = list(
    OutboundEmail.objects.filter(source_recommendation=rec)
    .order_by("-created_at")
    .values(
        "id",
        "email_type",
        "status",
        "opportunity_id",
        "source_inbound_id",
        "source_recommendation_id",
        "created_at",
    )
)

print("Recommendation status after first:", rec.status)
print("Outbound total after first:", after_first_total)
print("Linked to rec after first:", len(linked_after_first))
for row in linked_after_first:
    print(row)

print("\n=== SECOND EXECUTION ===")
request_2 = rf.post(f"/recommendations/{rec.id}/execute-followup/")
response_2 = execute_followup(request_2, rec.id)
print("Response 2 status:", response_2.status_code)
print("Response 2 location:", response_2["Location"])

rec.refresh_from_db()

after_second_total = OutboundEmail.objects.count()
linked_after_second = list(
    OutboundEmail.objects.filter(source_recommendation=rec)
    .order_by("-created_at")
    .values(
        "id",
        "email_type",
        "status",
        "opportunity_id",
        "source_inbound_id",
        "source_recommendation_id",
        "created_at",
    )
)

print("Recommendation status after second:", rec.status)
print("Outbound total after second:", after_second_total)
print("Linked to rec after second:", len(linked_after_second))
for row in linked_after_second:
    print(row)

print("\n=== RESULT ===")
print({
    "created_on_first_run": after_first_total - before_total,
    "created_on_second_run": after_second_total - after_first_total,
    "final_status": rec.status,
    "linked_count": len(linked_after_second),
})
