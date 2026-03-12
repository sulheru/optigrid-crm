from pathlib import Path

path = Path("/home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/emailing/views.py")
text = path.read_text()

start = text.index("def opportunities_list_view(request):")
end = text.index("\n\n@require_POST\ndef opportunity_set_stage_view", start)

new_block = '''def opportunities_list_view(request):
    opportunities_qs = Opportunity.objects.all()

    stage = (request.GET.get("stage") or "").strip()
    requested_sort = (request.GET.get("sort") or "-updated_at").strip()
    sort = OPPORTUNITY_ALLOWED_SORTS.get(requested_sort, "-updated_at")

    if stage and stage in OPPORTUNITY_STAGE_CHOICES:
        opportunities_qs = opportunities_qs.filter(stage=stage)

    if sort in ("estimated_value", "-estimated_value"):
        descending = sort.startswith("-")
        opportunities_qs = opportunities_qs.order_by(
            F("estimated_value").desc(nulls_last=True) if descending else F("estimated_value").asc(nulls_last=True),
            F("updated_at").desc(nulls_last=True),
        )
    elif sort in ("confidence", "-confidence"):
        descending = sort.startswith("-")
        opportunities_qs = opportunities_qs.order_by(
            F("confidence").desc(nulls_last=True) if descending else F("confidence").asc(nulls_last=True),
            F("updated_at").desc(nulls_last=True),
        )
    else:
        opportunities_qs = opportunities_qs.order_by(sort)

    opportunities = list(opportunities_qs)

    for opportunity in opportunities:
        opportunity.available_next_stages = OPPORTUNITY_STAGE_TRANSITIONS.get(opportunity.stage, [])

    stage_counts = {stage_name: 0 for stage_name in OPPORTUNITY_STAGE_CHOICES}
    total_estimated_value = 0
    estimated_value_count = 0
    confidence_total = 0.0
    confidence_count = 0

    for opportunity in opportunities:
        if opportunity.stage in stage_counts:
            stage_counts[opportunity.stage] += 1

        if opportunity.estimated_value is not None:
            total_estimated_value += opportunity.estimated_value
            estimated_value_count += 1

        if opportunity.confidence is not None:
            confidence_total += float(opportunity.confidence)
            confidence_count += 1

    average_confidence = round(confidence_total / confidence_count, 2) if confidence_count else None

    opportunity_columns = []
    if not stage:
        for stage_name in OPPORTUNITY_STAGE_CHOICES:
            items = [op for op in opportunities if op.stage == stage_name]
            opportunity_columns.append(
                {
                    "key": stage_name,
                    "label": stage_name.capitalize(),
                    "items": items,
                    "count": len(items),
                }
            )

    return render(
        request,
        "opportunities/list.html",
        {
            "opportunities": opportunities,
            "opportunity_columns": opportunity_columns,
            "current_stage": stage,
            "current_sort": requested_sort if requested_sort in OPPORTUNITY_ALLOWED_SORTS else "-updated_at",
            "stage_choices": OPPORTUNITY_STAGE_CHOICES,
            "total_results": len(opportunities),
            "metrics": {
                "total_opportunities": len(opportunities),
                "total_estimated_value": total_estimated_value,
                "estimated_value_count": estimated_value_count,
                "average_confidence": average_confidence,
                "new_count": stage_counts["new"],
                "qualified_count": stage_counts["qualified"],
                "proposal_count": stage_counts["proposal"],
                "won_count": stage_counts["won"],
                "lost_count": stage_counts["lost"],
            },
        },
    )
'''

updated = text[:start] + new_block + text[end:]
path.write_text(updated)
print("OK: opportunities_list_view actualizada.")
