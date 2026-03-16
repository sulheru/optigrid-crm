## Session — 2026-03-16

### Objective
Implement **Opportunity Intelligence Layer V1** allowing opportunities to be analyzed using full CRM pipeline context.

### Work Completed

Implemented management command:

    python manage.py analyze_opportunity <id>

The command now reconstructs full context chain:

Opportunity
→ source_task
→ source_recommendation
→ inference
→ fact
→ email

Context builder now supports reverse lineage reconstruction:

InferenceRecord
→ FactRecord (via source_type=fact_record)
→ EmailMessage (via source_type=email_message)

### Example Output

Opportunity #1 context:

inferences: 1
facts: 1
emails: 1

Detected reasoning chain:

Email:
"Ahora no, escríbeme en mayo y lo retomamos."

Fact extracted:
timing_statement

Inference derived:
next_best_action = follow_up_later (may)

Generated recommendations:

- followup
- risk_flag
- next_action

### Improvements Added

Context builder improvements:

- scope_type alias normalization
- reverse lineage reconstruction
- safe model resolution
- deduplicated entity loading
- email/thread discovery
- contextual summary generation

### Result

Opportunity Intelligence Layer V1 is now operational.

Opportunities can be analyzed using:

- email signals
- extracted facts
- derived inferences
- existing recommendations
- task context

without breaking the existing CRM pipeline.

### Status

STABLE
Ready for batch analysis and UI integration.
