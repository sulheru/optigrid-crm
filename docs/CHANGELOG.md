# CHANGELOG

## 2026-03-22

### OptiGrid CRM — Execute Reliability + Unified Execute + Cockpit Prep

#### Recomendations / Execute
- Se estabilizó `execute_followup` para evitar duplicados mediante reutilización de drafts existentes.
- Se consolidó el uso del estado `executed` en `AIRecommendation`.
- Se añadió ejecución real para `contact_strategy`:
  - genera o reutiliza `OutboundEmail` de tipo `first_contact`
  - marca la recommendation como `executed`
- Se añadió ejecución real para `reply_strategy`:
  - reutiliza o genera `followup` sobre el inbound más reciente
  - marca la recommendation como `executed`

#### Execute unificado
- Se implementó endpoint unificado:
  - `/recommendations/<id>/execute/`
- El endpoint enruta internamente por `recommendation_type` hacia:
  - `execute_followup`
  - `execute_contact_strategy`
  - `execute_reply_strategy`
- Se mantuvieron los endpoints específicos por compatibilidad.

#### Emailing / Models
- `OutboundEmail` conserva el campo:
  - `source_recommendation`
- Migraciones aplicadas correctamente:
  - `0008_outboundemail_source_recommendation`
  - `0008_inbounddecision_automation_fields`
  - `0009_merge_0008_emailing_branches`

#### Validaciones realizadas
- Verificada idempotencia en `contact_strategy`:
  - primera ejecución crea draft
  - segunda ejecución no duplica
  - recommendation termina en `executed`
- Verificado execute unificado:
  - enruta correctamente
  - no duplica en segunda ejecución
  - deja la recommendation en `executed`

#### Estado de dashboard / cockpit
- Confirmado que el dashboard actual sigue usando mapping manual parcial de acciones.
- Confirmado que ya existe base suficiente para pasar a cockpit V2C:
  - botón único `Execute`
  - urgency panel
  - activity feed
