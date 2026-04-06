# Sofía — Definición Arquitectónica

## Naturaleza

Sofía es el orquestador central del sistema.

No es:
- Core
- Plugin
- UI

Es:
- Entidad operativa
- Coordinadora de flujos
- Consumidora de capacidades

---

## Responsabilidades

- Observar contexto global
- Decidir qué flujo activar
- Coordinar workflows
- Construir contexto para IA
- Generar propuestas (no ejecutar)

---

## Limitaciones

- No puede modificar directamente el Core
- No puede ejecutar side effects
- No puede saltarse Update ni Execution Boundary

---

## Representación

SystemAgent:
- agent_key: "sofia"
- role: "central_orchestrator"
