# CHANGELOG

## [Session] Mail Provider Layer Integration + Knowledge Stabilization

### Added
- Runtime settings system
- Execution adapter registry
- Provider abstraction for mail
- prepare_mail_provider_context()
- normalized_preview in ExternalActionIntent
- inbound-based resolution (thread + account)

### Changed
- Replaced flat payloads with provider-aware payloads
- Integrated provider layer into recommendation → intent flow
- Enhanced dispatcher with guardrails

### Fixed
- Knowledge models inconsistencies
- VectorMemoryItem field errors
- KnowledgeCandidate enum mismatch
- Broken migrations

### Improved
- Observability of external intents
- Multi-account readiness
- Thread continuity handling

### Security / Guardrails
- Explicit block on EMAIL_SEND
- Draft-only execution enforced

