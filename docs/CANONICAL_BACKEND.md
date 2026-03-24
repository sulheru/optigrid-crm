# CANONICAL BACKEND
## OptiGrid CRM — AI Commercial Operating System

Estado: draft operativo aprobado para implementación  
Fecha: 2026-03-24  
Fase: Control y Canonical Backend

---

# 1. Propósito

Este documento define el backend canónico del sistema.

Su función es fijar, antes de refactorizar más, qué flujo es el oficial, qué capas existen, qué responsabilidades tiene cada una y qué partes del backend actual deben considerarse transitorias.

Objetivo:

Pasar de un backend funcional pero mezclado a un backend con:

- pipeline único
- responsabilidad clara por capas
- execution centralizado
- simulation aislada
- terreno preparado para:
  - MailProvider
  - LLMProvider
  - CalendarProvider
  - SOI

---

# 2. Hallazgos confirmados

El sistema actual contiene dos pipelines reales.

## 2.1 Pipeline semántico canónico ya existente

Existe un pipeline horizontal en `services/`:

`EmailMessage -> FactRecord -> InferenceRecord -> CRMUpdateProposal -> AIRecommendation`

Esto está implementado en:

- `services/email_ingest.py`
- `services/fact_extraction.py`
- `services/inference_engine.py`
- `services/update_proposals.py`

Este pipeline representa el backbone conceptual correcto del sistema.

## 2.2 Pipeline paralelo de Inbox Intelligence

Existe un pipeline vertical en `apps/emailing/services/`:

`InboundEmail -> InboundInterpretation -> InboundDecision -> apply`

Este pipeline:

- interpreta
- decide
- aplica directamente

y puede:

- crear `OutboundEmail`
- crear `CRMTask`
- cambiar `Opportunity.stage`

sin pasar por:

- `FactRecord`
- `InferenceRecord`
- `CRMUpdateProposal`
- `AIRecommendation`

## 2.3 Conclusión arquitectónica

El sistema no está roto.

El sistema tiene:

- un core correcto
- un shortcut operativo paralelo

La siguiente fase no consiste en rehacer todo, sino en consolidar el atajo dentro del canon.

---

# 3. Decisión canónica

## 3.1 Pipeline oficial del sistema

A partir de esta sesión, el pipeline oficial del backend será:

`InputSignal -> FactRecord -> InferenceRecord -> CRMUpdateProposal -> AIRecommendation -> Execution`

## 3.2 Regla principal

Toda entrada relevante del sistema debe terminar expresada en el core semántico antes de ejecutarse.

Toda acción ejecutable del sistema debe salir desde una `AIRecommendation` o desde una abstracción formal equivalente futura.

## 3.3 Traducción operativa

Esto implica:

- ningún flujo importante debe aplicar cambios de negocio directamente desde una interpretación local
- `emailing` deja de ser un cerebro alternativo
- `emailing` pasa a ser un adapter/application workflow especializado
- `recommendations` pasa a ser el punto oficial de decisión ejecutable
- la ejecución debe converger en una capa central

---

# 4. Modelo canónico por capas

## 4.1 Domain layer

Contiene entidades de negocio y persistencia estructurada.

Entidades actuales relevantes:

- `EmailMessage`
- `InboundEmail`
- `OutboundEmail`
- `FactRecord`
- `InferenceRecord`
- `CRMUpdateProposal`
- `AIRecommendation`
- `CRMTask`
- `Opportunity`

Regla:

El dominio almacena hechos, inferencias, propuestas, recomendaciones y resultados.
No debe contener lógica de integración externa incrustada.

## 4.2 Application layer

Contiene workflows y casos de uso.

Casos de uso canónicos objetivo:

- ingest raw email signal
- interpret inbound signal
- materialize facts
- materialize inferences
- materialize proposals
- materialize recommendations
- execute recommendation
- promote task to opportunity
- generate strategy answer

Regla:

La application layer orquesta el flujo.
No debe mezclar UI ni detalles de provider real/simulado.

## 4.3 Provider layer

Contiene implementaciones concretas intercambiables.

Ejemplos actuales implícitos:

- mail simulation
- Gemini strategy backend
- M365 graph client
- future Outlook mail sender
- future Calendar provider

Regla:

Todo acceso a mundo externo debe vivir aquí o estar preparado para moverse aquí.

## 4.4 Interface layer

Contiene:

- Django views
- management commands
- admin
- future API endpoints
- strategic chat surface

Regla:

Las interfaces llaman casos de uso.
No ejecutan negocio profundo directamente.

## 4.5 Orchestration layer futura

No se implementa todavía en esta fase, pero el canon la prepara.

Futuras piezas:

- SOI
- policy router
- simulation/real mode router
- multi-provider dispatch

---

# 5. Pipeline canónico detallado

## 5.1 Entrada

Un input del sistema puede venir de:

- `EmailMessage`
- `InboundEmail`
- lead research
- manual supervisor action
- future calendar event
- future provider signal

Todos ellos deben converger conceptualmente en `InputSignal`.

## 5.2 Facts

`FactRecord` representa observables estructurados.

Regla:

- facts describen lo que ocurrió
- facts no son decisiones
- facts no aplican cambios

## 5.3 Inferences

`InferenceRecord` representa interpretación operativa derivada.

Regla:

- una inferencia explica una posible lectura del hecho
- una inferencia no ejecuta
- una inferencia no muta el CRM directamente

## 5.4 Proposals

`CRMUpdateProposal` representa cambio sugerido sobre entidades CRM.

Regla:

- proposals son cambios sugeridos
- proposals no son todavía acción final
- proposals permiten trazabilidad y governance

## 5.5 Recommendations

`AIRecommendation` es la unidad operativa ejecutable del sistema.

Regla:

- las acciones del sistema deben salir de aquí
- ranking, urgency, NBA y explainability viven sobre recommendations
- la UI ejecuta recommendations, no decisiones locales ocultas

## 5.6 Execution

Execution transforma recomendación en efecto material.

Ejemplos:

- draft outbound
- task
- promotion to opportunity
- stage change
- future calendar action

Regla:

La ejecución debe estar centralizada detrás de un contract explícito.

---

# 6. Qué es core y qué no

## 6.1 Core canónico

Se consideran core canónico:

- `facts`
- `inferences`
- `updates`
- `recommendations`
- `tasks`
- `opportunities`

## 6.2 Workflows especializados, no core

Se consideran workflows/adapters especializados:

- `apps/emailing`
- `apps/strategy`
- `apps/lead_research`

## 6.3 Simulación, no core

Se consideran simulation adapters:

- `apps/emailing/services/inbound_simulator.py`
- `apps/recommendations/simulation.py`

Regla:

La simulación nunca debe definir la arquitectura.
Solo debe implementarla en modo fake/test/demo.

---

# 7. Problemas actuales que este canon corrige

## 7.1 Doble cerebro

Hoy conviven:

- pipeline facts/inferences/updates/recommendations
- pipeline interpretation/decision/apply

Esto fragmenta la lógica.

## 7.2 Apply directo desde emailing

`inbound_decision_apply_service.py` crea drafts, tasks y cambios de oportunidad de forma directa.

Eso hace que la ejecución no pase por el core semántico.

## 7.3 Simulation mezclada con envío

`outbound_sender.py` envía y luego simula reply.
Eso indica que simulation está embebida donde en el futuro habrá provider real.

## 7.4 Recommendations parciales

`AIRecommendation` ya existe como entidad operativa, pero no toda la acción del sistema fluye todavía por ella.

---

# 8. Contratos canónicos objetivo

Estos contratos se fijan ya, aunque algunos se implementen progresivamente.

## 8.1 InputSignal

Representa una señal entrante normalizada.

Campos conceptuales mínimos:

- `source_kind`
- `source_id`
- `channel`
- `payload`
- `received_at`

Nota:
No hace falta crear aún el modelo definitivo si todavía no conviene.
Pero sí debe convertirse en abstracción mental oficial.

## 8.2 Fact contract

Salida estructurada de observación.

Campos clave:

- `source_type`
- `source_id`
- `fact_type`
- `fact_value`
- `observed_at`
- `confidence`

## 8.3 Inference contract

Salida estructurada de interpretación.

Campos clave:

- `source_type`
- `source_id`
- `inference_type`
- `inference_value`
- `confidence`
- `rationale`

## 8.4 Proposal contract

Salida estructurada de cambio CRM sugerido.

Campos clave:

- `target_entity_type`
- `target_entity_id`
- `proposed_change_type`
- `proposed_payload`
- `confidence`
- `approval_required`
- `proposal_status`

## 8.5 Recommendation contract

Unidad operativa central.

Campos clave existentes/relevantes:

- `scope_type`
- `scope_id`
- `recommendation_type`
- `recommendation_text`
- `confidence`
- `status`

Campos operativos ya usados por ranking:

- `priority_score`
- `urgency_score`
- `type_weight`
- `global_score`
- `decision_quality_score`
- `actionability_bonus`

## 8.6 ExecutionResult contract

Debe existir como contrato de salida de la ejecución.

Campos objetivo:

- `executor`
- `recommendation_id`
- `status`
- `created_entities`
- `updated_entities`
- `side_effects`
- `errors`

No hace falta todavía un modelo persistido si no conviene.
Sí hace falta una forma estable de retorno.

---

# 9. Regla de oro de ejecución

## 9.1 Regla

Ninguna vista ni workflow vertical debe ejecutar acciones materiales de negocio sin pasar por una capa de ejecución central.

## 9.2 Implicación inmediata

Estas formas quedan conceptualmente deprecadas:

- `emailing -> decision -> apply direct`
- `view -> create task directly`
- `view -> create opportunity directly`

## 9.3 Forma objetivo

La forma objetivo es:

`Recommendation -> ExecutionService -> domain effects`

---

# 10. Plan de implementación para esta fase

## 10.1 Fase 1A — fijar canon
Estado: este documento

## 10.2 Fase 1B — introducir execution service canónico
Objetivo:

Crear una capa única de ejecución que reciba una recomendación y produzca efectos.

Ejemplo conceptual:

- `execute_recommendation(recommendation)`
- delega internamente según `recommendation_type`
- devuelve `ExecutionResult`

## 10.3 Fase 1C — hacer que emailing deje de aplicar directo
Objetivo:

Sustituir el patrón:

`Interpretation -> Decision -> Apply`

por:

`Inbound signal -> semantic pipeline -> AIRecommendation -> execute`

## 10.4 Fase 1D — separar simulation de sender
Objetivo:

El sender no debe decidir la simulación.
La simulación debe vivir detrás de un adapter o modo de ejecución.

## 10.5 Fase 1E — preparar interfaces provider
Objetivo:

Cuando el canon esté consolidado:

- `MailProvider`
- `LLMProvider`
- `CalendarProvider`

pero sin implementar aún Outlook/Calendar real.

---

# 11. Decisiones de implementación inmediata

A partir de esta sesión, se adoptan estas decisiones:

## D1
`facts -> inferences -> updates -> recommendations` es el pipeline semántico oficial.

## D2
`AIRecommendation` es la entidad operativa oficial para acción ejecutable.

## D3
La ejecución debe concentrarse detrás de una capa única, no repartida por views o workflows verticales.

## D4
`apps/emailing` deja de considerarse backend autónomo; pasa a ser workflow especializado y transitorio hasta converger con el canon.

## D5
Simulation se considera adapter de entorno, no parte del core.

## D6
No se implementarán todavía:
- Outlook real
- Calendar real
- SOI completo

---

# 12. Qué se considera éxito en esta fase

La fase se considerará correctamente encaminada cuando:

- el inbox pipeline deje de bypassear facts/inferences/recommendations
- exista un execution entrypoint central
- las views llamen a casos de uso, no a lógica dispersa
- simulation quede desacoplada del sender
- el backend esté listo para abstraerse en providers

---

# 13. Resumen ejecutivo

El sistema actual ya contiene el núcleo correcto.

Lo que faltaba no era potencia, sino canon.

El canon definido aquí fija que:

- el core del sistema es semántico
- las recomendaciones son la unidad de acción
- la ejecución debe ser central
- emailing no puede seguir siendo un cerebro alternativo
- simulation no puede seguir mezclada con operación

Este documento convierte el backend actual en una arquitectura con dirección clara.

