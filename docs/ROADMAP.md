# ROADMAP

## Estado actual
### Fases cerradas
- Rule Engine determinista
- RULE_TRACE estructurado
- Explainability layer
- Decision Output layer
- Persistencia de trace y decisión operativa
- Inbox Decision Panel integrado
- Decision Detail Trace Recovery
- Auditoría inicial de readiness para providers / LLM / pluginización

## Hallazgo estratégico actual
El sistema ya dispone de una base arquitectónica suficiente para plantear pluginización, pero el core aún no está cerrado para operación real completa.

La decisión tomada es:

**no empezar aún la fase de plugins**
hasta cerrar primero el núcleo operativo real.

## Nueva fase inmediata
### Core Operational Closure

Objetivo:
cerrar el core completo para operación real antes de introducir el sistema de plugins de Sofía.

### Qué significa “core completo” aquí
El core debe quedar preparado para:
- identidad operativa canónica de mailbox / tenant / cuenta
- ejecución real de acciones
- separación completa entre decisión y ejecución
- providers reales de correo
- configuración operativa consistente
- producción controlada

### Bloques a cerrar
1. **Canonical Mailbox Identity**
   - persistencia canónica de mailbox / tenant / operating organization
   - eliminación de heurísticas frágiles en resolución de cuenta

2. **Execution Engine**
   - puente explícito decisión → acción
   - apply real con policy, trazabilidad y errores controlados

3. **Real Mail Providers**
   - SMTP real
   - M365 real
   - mantener SMLL encajado sin acoplamiento impropio

4. **Provider / Runtime Convergence**
   - unificar runtime, registry y resolución de cuentas/providers
   - definir capacidades reales por provider

5. **Operational Readiness**
   - health, errores, límites, seguridad operativa
   - base suficientemente estable para producción

## Criterio de cierre de fase
La fase se considerará cerrada cuando:
- el sistema pueda resolver identidad operativa de correo de forma canónica
- pueda materializar drafts/acciones por una capa de ejecución real
- exista al menos un provider de correo real plenamente funcional
- decisión y ejecución estén separadas y conectadas de forma explícita
- el sistema esté listo para empezar pluginización sin reabrir el core

## Fase posterior
### Plugin System / Sofía OS

Solo después del cierre del core operativo.

### Objetivo de esa fase posterior
- convertir capacidades en plugins formales
- distinguir plugins fijos vs removibles
- navegación dinámica
- manifests, lifecycle y config por plugin

## Nota estratégica
El sistema ya no necesita más refactor conceptual del motor de decisión.
La prioridad ya no es UI.
La prioridad inmediata es:
**cerrar operación real del core**.
