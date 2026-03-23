# NEXT SESSION

## Objetivo
Iniciar la FASE A — CONTROL Y CANONICAL BACKEND.

## Contexto
La auditoría de hoy ha confirmado que el sistema ya tiene backend potente, pero todavía no suficientemente unificado.

Conviven:
- pipeline facts/inferences/proposals/recommendations
- inbox intelligence / decision / apply
- simulación embebida en emailing
- strategy backend parcial
- execution layer funcional

Antes de empezar con SOI, Outlook o LLM plugins completos, hay que consolidar el backend canónico.

---

## Objetivos concretos de la siguiente sesión

### 1. Definir pipeline canónico
Aclarar:
- cuál es el flujo principal real del sistema
- cómo encajan:
  - email_ingest
  - facts
  - inferences
  - updates
  - recommendations
  - inbox intelligence
  - execution

### 2. Diseñar target backend structure
Separar mental y estructuralmente:
- domain models
- application services
- providers/adapters
- orchestration
- views

### 3. Identificar acoplamientos
Buscar puntos donde hoy esté mezclado:
- simulación con core
- views con lógica de aplicación
- recommendations con UI decoration
- execution con provider implícito

### 4. Preparar provider abstraction layer
Sin implementarla completa aún, dejar definido qué contratos harán falta:
- MailProvider
- LLMProvider
- CalendarProvider
- SOI

---

## Regla de trabajo
No asumir nada.
Leer primero.
No implementar plugins todavía.
No abrir Outlook todavía.
No refactorizar a ciegas.

Primero control backend.

