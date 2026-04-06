# Platform Layers Contract

## Capas del sistema

1. Core
2. Application
3. Sofia Orchestration
4. Access
5. EIL (External/Internal Ingestion Layer)
6. I/O Hooks
7. Plugins
8. Event Bus
9. Workflows
10. Update Boundary
11. Execution Boundary

---

## Reglas globales

- Ninguna capa puede saltarse una frontera crítica
- Toda entrada externa debe pasar por EIL
- Todo cambio estructural pasa por Update Boundary
- Toda acción externa pasa por Execution Boundary
- Sofía coordina, pero no define el dominio
- El Core define la verdad del sistema
- Los plugins extienden, no gobiernan

---

## Regla de dependencias

- Core no depende de nadie
- Application depende de Core
- Sofía depende de Application
- Access depende de Sofía/Application
- Workflows reaccionan a eventos
- Update y Execution son fronteras obligatorias
