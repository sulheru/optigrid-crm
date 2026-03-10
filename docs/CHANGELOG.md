# OptiGrid CRM — CHANGELOG

## 2026-03-10 — Opportunity Engine & Observability

### Added

AI Opportunity Engine (V1):

- New action: **Promote Recommendation → Opportunity**
- Route: `/recommendations/<id>/promote-opportunity/`
- Security rules to avoid promotion of dismissed recommendations
- Basic deduplication logic for opportunities

### UI Improvements

Recommendations UI:

- Visual badge system for recommendation types
- Highlight for `opportunity_review`
- Button **Promote to Opportunity**

Opportunities UI:

- New layout showing:
  - title
  - company_name
  - stage
  - confidence
  - estimated_value
  - summary
  - created_at / updated_at

### Observability

New management command:


python manage.py crm_pipeline_report


Provides:

- Pipeline totals
- Recommendations by status
- Recommendations by type
- Recommendations by confidence buckets
- Tasks by status
- Tasks by type
- Tasks by priority
- Opportunities by stage

### Architecture

Pipeline now supports:

EmailMessage  
→ FactRecord  
→ InferenceRecord  
→ CRMUpdateProposal  
→ AIRecommendation  
→ CRMTask  
→ Opportunity

Recommendations can now be promoted directly to opportunities.

This marks the beginning of the **AI Opportunity Engine layer**.
