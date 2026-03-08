
## 2026-03-08

### Added

AIRecommendation generation from inference records.

New module:

apps/recommendations/services.py

Pipeline extended:

EmailMessage → FactRecord → InferenceRecord → CRMUpdateProposal → AIRecommendation

### Fixed

Repaired broken pipeline integration in:

services/email_ingest.py

Rebuilt demo command:

apps/emailing/management/commands/demo_email_flow.py

### Verified

End-to-end demo scenarios:

interest  
redirect  
timing  
budget  
light

All scenarios generate expected facts, inferences, proposals and recommendations.

