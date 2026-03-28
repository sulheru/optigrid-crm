# CHANGELOG — SESSION CORE CONTROL LAYER

## Added

- Central factory for AIRecommendation creation
- ExternalActionIntent full lifecycle:
  - approval
  - dispatch
- Inbound decision → recommendation bridge (restored)

## Changed

- Execution layer unified under execute_recommendation_service
- Inbound pipeline:
  - scope_type moved from inbound_decision → inbound_email
  - action mapping normalized

## Fixed

- Broken inbound execution (no opportunity resolution)
- Draft creation failure (OutboundEmail not created)
- Recommendation deduplication issues
- Multiple creation paths for AIRecommendation

## Removed / Deprecated

- Direct AIRecommendation.objects.create in production paths
- Legacy creation flows (kept only in tests)

## Known Issues

- apps.knowledge.tests failing due to missing models:
  - BehaviorEntry
  - FAQEntry
  - VectorMemoryItem
