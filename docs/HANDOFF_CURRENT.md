# OptiGrid CRM — Current State

## System Status

Pipeline is fully operational:

Email → Facts → Inferences → Proposals → Recommendations → Tasks → Opportunities

Opportunity Intelligence Layer V1 has been added.

## New Capability

Command:

python manage.py analyze_opportunity <id>

The command:

1. Reconstructs opportunity context
2. Traverses lineage backwards
3. Extracts signals from:

- inferences
- facts
- emails

4. Generates new AI recommendations.

## Context Reconstruction

Current lineage model:

AIRecommendation
→ InferenceRecord
→ FactRecord
→ EmailMessage

Example:

Email:
"Ahora no, escríbeme en mayo"

Fact:
timing_statement

Inference:
next_best_action = follow_up_later

Recommendation:
followup

## Key Files

apps/opportunities/management/commands/analyze_opportunity.py  
apps/opportunities/services/context_builder.py  

## Stability

Stable.

No existing pipeline components were modified.

## Next Logical Steps

1. Batch opportunity analysis
2. UI integration
3. Recommendation materialization rules
