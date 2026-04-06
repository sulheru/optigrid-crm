# Refactor Gap Analysis

## Objetivo
Detectar violaciones de arquitectura en el sistema actual.

---

## 1. Acceso directo al dominio
- [ ] Views escribiendo modelos directamente
- [ ] Servicios saltándose Update Boundary

## 2. Mezcla de responsabilidades
- [ ] Providers con lógica de negocio
- [ ] Parsing + decisión + ejecución mezclados

## 3. Side effects no controlados
- [ ] Envíos directos sin Execution Boundary
- [ ] Llamadas externas desde capas incorrectas

## 4. IA mal ubicada
- [ ] Lógica LLM mezclada con reglas deterministas
- [ ] Decisiones sin pasar por fronteras

---

## Resultado
Lista priorizada de fugas arquitectónicas
