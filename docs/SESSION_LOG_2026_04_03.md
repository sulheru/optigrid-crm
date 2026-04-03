# SESSION LOG — 2026-04-03

## Tema
OptiGrid CRM — Auditoría de readiness para plugins y decisión de cierre previo del core operativo

## Resumen ejecutivo
La sesión comenzó explorando la idea de Sofía / S.O.F.I.A. como sistema operativo IA con módulos tipo plugin.

Se definió primero una dirección arquitectónica:
- plugins fijos vs plugins removibles
- SMLL y SMTP como piezas estructurales
- M365 y futuros providers como plugins opcionales

Sin embargo, tras auditar ficheros reales del sistema, se decidió no abrir todavía la fase de plugins y priorizar antes el cierre del core para operación real completa.

## Trabajo realizado

### 1. Decisión conceptual sobre Sofía
Se consolidó esta idea:
- Sofía será la identidad operativa del sistema
- las capacidades se formalizarán como plugins
- no todos los plugins serán desinstalables
- existirán plugins fijos y plugins opcionales

### 2. Auditoría de ficheros reales
Se revisaron:
- `config/settings.py`
- `apps/core/runtime_settings.py`
- `apps/emailing/services/mail_provider_service.py`
- `apps/emailing/services/provider_router.py`
- `apps/providers/registry.py`
- `apps/providers/mail_registry_v2.py`
- `apps/providers/mail_runtime.py`
- `apps/providers/mail_embedded.py`
- `apps/providers/mail_m365.py`
- `apps/providers/llm_embedded.py`
- `apps/providers/llm_gemini.py`
- `templates/base.html`
- `templates/partials/app_sidebar.html`

### 3. Hallazgos principales
#### A. Existe base de provider abstraction
Hay:
- runtime config
- runtime account resolution
- provider selection
- interfaz base suficiente para empezar pluginización más adelante

#### B. Sidebar completamente hardcodeado
La UI aún no descubre capacidades del sistema.
La navegación sigue escrita manualmente en plantilla.

#### C. SMLL está funcional pero mal posicionado
`provider_router.py` sigue acoplando resolución de mailbox, adaptación SMLL y respuesta simulada.

#### D. Mailbox identity no está cerrada
El propio código reconoce que `InboundEmail/Opportunity` aún no persisten tenant/mailbox de forma canónica.

#### E. M365 no está operativo
Sigue siendo stub.
No existe provider real de correo listo para producción.

#### F. Execution layer aún no está cerrada
Existe `prepare_provider_draft`, pero todavía no un execution engine completo.

### 4. Conclusión de arquitectura
El sistema está:
- suficientemente maduro para pensar en plugins
- no suficientemente cerrado para construir plugins encima sin riesgo de reabrir el núcleo

### 5. Decisión tomada
Se aplaza la fase de plugins.

Nueva prioridad:
**cerrar el core operativo real antes de empezar pluginización**

## Resultado neto
Queda abierta una nueva fase:

### Core Operational Closure

## Próximo paso decidido
La siguiente sesión debe centrarse en:
1. canonical mailbox identity
2. decision → execution boundary
3. mínimo execution engine necesario
4. orden de cierre restante del core
