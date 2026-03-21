# ROADMAP — OptiGrid CRM

## VISIÓN
Construir un AI Commercial Operating System donde la IA:
- interpreta señales
- propone acciones
- ejecuta trabajo comercial real
- deja al usuario en rol de CEO / supervisor

---

## ESTADO ACTUAL

### Backend
- Automation Layer V3 completo
- scoring / priority / risk_flags persistidos
- auto-apply con policy
- decisiones auditadas
- dedupe funcional en partes previas del pipeline
- pipeline end-to-end operativo

### UI
- UI FOUNDATION V1 completado
- UI FOUNDATION V2A completada
- aplicación unificada sobre `base.html`
- dashboard convertido en cockpit inicial
- strategic chat integrado
- inbox / outbox / recommendations / tasks / leads normalizados

### Cockpit
- V2B Phase 1 completada:
  - AI Recommended Actions en dashboard
  - priorización por confidence
  - mapping semántico de recommendation_type
  - Execute real para followup

---

## FASES

### Fase 1 — UI FOUNDATION V1
✅ completada

### Fase 2 — UI FOUNDATION V2A
✅ completada
- consistencia visual
- eliminación de deuda en pantallas activas
- limpieza de templates legacy críticos

### Fase 3 — UI FOUNDATION V2B
🟡 en curso

#### V2B Phase 1
✅ completada
- AI Recommended Actions
- dashboard como centro de decisiones
- primer execute real

#### V2B Phase 2
🔜 siguiente
- evitar duplicados
- executed state
- execute real multi-tipo

#### V2B Phase 3
🔜 posterior
- urgency panel
- activity feed
- quick actions
- strategic chat accionable

---

## SIGUIENTE HITO
### Execute fiable
- deduplicación
- estado executed
- trazabilidad

### Después
### Execute ampliado
- reply_strategy
- contact_strategy
- pricing/timing strategy
- risk flag handling

---

## OBJETIVO ESTRATÉGICO INMEDIATO
Evolucionar de:

CRM con IA  
→ cockpit con acciones  
→ sistema que ejecuta trabajo comercial con supervisión humana

---

## PRINCIPIO DE IMPLEMENTACIÓN
- no hacer suposiciones
- validar contexto antes de tocar código
- usar `tmp/` para inspección y checks
- evitar sobreescrituras ciegas de views complejas
- priorizar cambios incrementales y seguros
