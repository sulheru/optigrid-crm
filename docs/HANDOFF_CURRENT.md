# HANDOFF CURRENT

## Proyecto
OptiGrid CRM

## Fecha de cierre
2026-04-03

## Fase actual
Auditoría técnica realizada.
Nueva fase activa:
**Core Operational Closure**

## Decisión estratégica cerrada
Se aplaza la fase de plugins de Sofía.

Aunque ya existe base suficiente para pluginización:
- runtime settings
- provider abstraction
- registry base
- UI shell estable

el core aún no está cerrado para operación real completa.

Por tanto, la prioridad inmediata pasa a ser cerrar primero el núcleo operativo real del sistema.

## Estado real consolidado

### Cerrado y sólido
- Rule Engine determinista
- RULE_TRACE estructurado
- Explainability layer
- Decision Output layer
- contrato semántico backend ↔ UI en `Decision Detail`
- base inicial de provider abstraction
- runtime settings con override en BD

### Parcial pero existente
- resolución runtime de cuentas de correo
- provider registry
- provider runtime para drafts
- LLM abstraction con provider embebido y Gemini
- integración SMLL funcional pero acoplada

### No cerrado aún
- mailbox / tenant / account como identidad operativa canónica
- execution engine real
- provider de correo real listo para producción
- separación convergida decisión → ejecución
- sidebar / UI guiado por capacidades/plugins
- plugin system formal

## Hallazgos técnicos clave

### 1. Mailbox identity no canónica
`provider_router.py` sigue resolviendo mailbox mediante heurísticas y reconoce explícitamente que `InboundEmail/Opportunity` aún no persisten tenant/mailbox de forma canónica.

### 2. Execution aún no existe como capa completa
`prepare_provider_draft` es una buena base, pero no equivale todavía a un execution engine real.

### 3. Providers no reales
- `embedded` crea drafts stub
- `m365` sigue stubbed
- SMTP aún no existe como provider real

### 4. Sidebar completamente hardcodeado
La navegación aún no refleja capacidades del sistema.

### 5. Registry/runtime aún no convergidos del todo
Existe base, pero todavía no un modelo formal único de capacidades, lifecycle y health.

## Nueva prioridad inmediata
Cerrar el core para operación real completa en este orden:

1. canonical mailbox identity
2. execution engine
3. real mail providers
4. convergence runtime/provider
5. production readiness básica

## Qué no hacer ahora
- no empezar aún manifests de plugins
- no hacer aún sidebar dinámico por plugins
- no abrir aún uninstall/install de plugins opcionales
- no entrar aún en Sofía OS como capa formal

## Condición para abrir la siguiente gran fase
Solo cuando el core operativo quede cerrado se abrirá:

### Plugin System / Sofía OS
con:
- plugins fijos
- plugins removibles
- navegación declarativa
- manifests
- health y lifecycle

## Riesgo abierto principal
Empezar plugins demasiado pronto congelaría sobre un núcleo todavía incompleto y obligaría a reabrir:
- mailbox model
- execution boundary
- provider contracts

La decisión tomada evita ese riesgo.
