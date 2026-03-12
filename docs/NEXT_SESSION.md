# OptiGrid CRM — Next Session

FASE: Opportunity Intelligence Layer

Fecha base: 2026-03-12

---

## Contexto

El CRM ya soporta pipeline completo:

Email
→ Facts
→ Inference
→ Proposals
→ Recommendations
→ Tasks
→ Opportunities

El siguiente paso es permitir que la IA analice **opportunities existentes**.

---

## Objetivo principal

Implementar **Opportunity Intelligence Engine**.

Esto permitirá generar recomendaciones desde una opportunity.

---

## Nuevo flujo

Opportunity
↓
AI Analysis
↓
AIRecommendation

Tipos previstos:

pricing_strategy
reply_strategy
followup
risk_flag
next_action

---

## Primera implementación

Añadir comando:

python manage.py analyze_opportunity <id>

El comando:

1. carga la opportunity
2. reconstruye contexto
3. genera recomendaciones

---

## Context reconstruction

Opportunity
↓
source_recommendation
↓
proposal
↓
inference
↓
facts
↓
emails

Esto permite reasoning completo.

---

## Resultado esperado

El CRM pasa de:

detectar oportunidades

a

asistir activamente en cerrar oportunidades.

---

## Verificaciones iniciales

Antes de empezar:

cd ~/OptiGrid_Project/og_pilot/optigrid_crm
source .venv/bin/activate

python manage.py check
python manage.py runserver

Verificar:

/recommendations/
/tasks/
/opportunities/

