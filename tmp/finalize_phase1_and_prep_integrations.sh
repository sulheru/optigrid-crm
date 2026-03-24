set -e

echo "=== 1. EXECUTION LAYER FILES ==="
sed -n '1,260p' apps/recommendations/execution.py
printf '\n\n=== execution_application.py ===\n'
sed -n '1,320p' apps/recommendations/execution_application.py
printf '\n\n=== execution_actions.py ===\n'
sed -n '1,320p' apps/recommendations/execution_actions.py
printf '\n\n=== execution_adapters.py ===\n'
sed -n '1,240p' apps/recommendations/execution_adapters.py

printf '\n\n=== 2. EXISTING PROVIDER/STUB CANDIDATES ===\n'
printf '\n--- services/m365/graph_client.py ---\n'
sed -n '1,260p' services/m365/graph_client.py || true
printf '\n--- services/ai/llm_client.py ---\n'
sed -n '1,260p' services/ai/llm_client.py || true
printf '\n--- apps/strategy/services/llm_backends.py ---\n'
sed -n '1,260p' apps/strategy/services/llm_backends.py || true
printf '\n--- apps/emailing/services/outbound_sender.py ---\n'
sed -n '1,220p' apps/emailing/services/outbound_sender.py || true
printf '\n--- apps/emailing/services/inbound_simulator.py ---\n'
sed -n '1,220p' apps/emailing/services/inbound_simulator.py || true

printf '\n\n=== 3. SETTINGS / ENV / FLAGS ===\n'
rg -n "GEMINI|GRAPH|M365|OUTLOOK|CALENDAR|MAIL_PROVIDER|LLM_PROVIDER|EXECUTION_MODE|EMAIL|MSAL|CLIENT_ID|TENANT|SECRET" \
  config apps services .env* || true

printf '\n\n=== 4. IMPORTS TO NEW EXECUTION LAYER ===\n'
rg -n "execute_recommendation_service|RecommendationExecutionError|from apps\.recommendations\.execution" apps services || true

printf '\n\n=== 5. RECOMMENDATION / INFERENCE ENTRYPOINTS ===\n'
printf '\n--- apps/inferences/services.py ---\n'
sed -n '1,220p' apps/inferences/services.py || true
printf '\n--- apps/recommendations/services.py ---\n'
sed -n '1,260p' apps/recommendations/services.py || true

printf '\n\n=== 6. TEST SAFETY PASS ===\n'
python3 manage.py test apps.emailing.tests apps.recommendations.tests apps.tasks.tests apps.opportunities.tests

printf '\n\n=== 7. GIT DIFF (TARGETED) ===\n'
git diff -- \
  apps/inferences/services.py \
  apps/recommendations/services.py \
  apps/recommendations/execution.py \
  apps/recommendations/execution_application.py \
  apps/recommendations/execution_actions.py \
  apps/recommendations/execution_adapters.py \
  apps/emailing/services/inbound_decision_apply_service.py \
  apps/emailing/services/recommendation_bridge.py \
  apps/recommendations/views.py \
  docs/CANONICAL_BACKEND.md || true
