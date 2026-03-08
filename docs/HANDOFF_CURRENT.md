# Handoff actual — OptiGrid CRM

## Fecha de referencia
2026-03-08

## Estado actual del proyecto

El proyecto ya dispone de un vertical slice funcional del pipeline IA-first de procesamiento de emails.

Pipeline operativo actual:

EmailMessage  
→ FactRecord  
→ InferenceRecord  
→ CRMUpdateProposal  
→ AIRecommendation

Además, ya existe una primera UI operativa de inspección del pipeline.

### Qué está implementado

- modelos base del pipeline
- extracción de hechos desde email
- generación de inferencias
- generación de propuestas de actualización CRM
- generación de recomendaciones IA
- comando demo funcional para escenarios de prueba
- interfaz web mínima para inspección del pipeline

### Qué está funcionando

- `python manage.py demo_email_flow`
- escenarios demo:
  - interest
  - redirect
  - timing
  - budget
  - light
- listado web de emails procesados en `/emails/`
- detalle de email en `/emails/<id>/`
- visualización de:
  - EmailMessage
  - Facts
  - Inferences
  - Proposals
  - Recommendations

### Qué sigue incompleto

- conteos enriquecidos en la lista con relaciones más precisas si se refinan los filtros
- navegación global más allá del módulo de emails
- dashboard inicial
- UI de recomendaciones y tareas
- integración real con Microsoft Graph / M365
- aplicación automática o supervisada de propuestas
- consola conversacional UI

---

## Decisiones cerradas en esta sesión

1. La primera UI a construir será la UI de inspección del pipeline.
2. La UI inicial se implementa con Django templates simples.
3. Se prioriza inspección funcional sobre diseño visual avanzado.
4. La primera navegación operativa se centra en emails procesados.
5. Se activa el directorio global `templates/` en `config/settings.py`.

---

## Cambios importantes respecto a la sesión anterior

- antes: el pipeline solo era verificable por consola y comandos demo
- ahora: el pipeline también es inspeccionable desde navegador
- antes: `HANDOFF_CURRENT.md` estaba desactualizado respecto al código real
- ahora: el estado documental se alinea con la implementación efectiva

---

## Arquitectura afectada

Capas afectadas en esta sesión:

### Interface layer
- nuevas vistas web para inspección

### Application layer
- vistas y urls de `apps/emailing`

### Presentation layer
- templates HTML para listado y detalle

### Configuración
- activación de `BASE_DIR / "templates"` en `config/settings.py`
- inclusión de rutas de emailing en `config/urls.py`

---

## Problemas abiertos

1. Los filtros de relación entre email, inferencias, propuestas y recomendaciones pueden refinarse para mayor precisión semántica.
2. La UI todavía es utilitaria y no tiene layout global del CRM.
3. No existe aún dashboard principal.
4. No existe aún vista específica de recomendaciones activas.
5. No existe aún vista de tareas ni de oportunidades.
6. No existe todavía autenticación/login como parte del flujo visible actual.

---

## Objetivo inmediato siguiente

Construir la segunda iteración de la UI operativa.

Prioridad recomendada:

1. mejorar `/emails/` con conteos completos y navegación más clara
2. refinar `/emails/<id>/` visualmente
3. crear dashboard mínimo
4. crear vista de recomendaciones activas

---

## Reglas activas del proyecto

- mantener separación entre hecho, inferencia, propuesta y recomendación
- no introducir complejidad frontend innecesaria
- seguir con Django templates como UI inicial
- priorizar vertical slices completos antes de expansión lateral
- mantener continuidad documental al final de cada sesión
