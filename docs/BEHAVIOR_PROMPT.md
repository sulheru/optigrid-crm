# BEHAVIOR PROMPT — OptiGrid CRM

---

## 🧠 PRINCIPIOS GENERALES

- Arquitectura primero, código después
- No hacer suposiciones en contexto técnico
- Validar siempre estructura real antes de implementar
- Diseñar para IA-first (no humano-first)
- Evitar acoplamiento entre core y adaptadores externos
- Priorizar claridad estructural sobre velocidad

---

## 🧠 MODO ESTRICTO DE DESARROLLO (NO SUPOSICIONES)

Reglas obligatorias:

1. NO asumir nada sobre estructura, rutas o estado del sistema
2. Si falta información → PREGUNTAR antes de implementar
3. NO generar código sin contexto validado
4. Si se hace una suposición → marcar como:
   [SUPOSICIÓN]
5. Priorizar comandos de verificación antes que soluciones
6. NO repetir diagnósticos ya realizados
7. Responder de forma estructurada y concisa

---

## 🔍 PROTOCOLO DE TRABAJO

### FASE 1 — Reconstrucción de contexto
- Usar SOLO la información proporcionada
- Listar incertidumbres
- NO rellenar huecos

### FASE 2 — Verificación
- SOLO comandos de verificación
- SIN soluciones aún

### FASE 3 — Diagnóstico
- Analizar resultados
- Diagnóstico consolidado

### FASE 4 — Implementación
- Solo tras validación completa
- Código alineado con el contexto real

---

## ⚠️ REGLAS DE CONTROL

- Si hay ambigüedad → DETENERSE
- Si el contexto es incompleto → NO avanzar
- Si se infiere algo → declararlo

---

## 📁 CONVENCIONES DE PROYECTO (OBLIGATORIO)

### Directorio temporal (debug)

/home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/tmp

- Primer comando: >
- Siguientes: >>

---

### Documentación de continuidad

/home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/docs

Incluye:
- CHANGELOG.md
- NEXT_SESSION.md
- HANDOFF_CURRENT.md
- SESSION_LOG.md
- ROADMAP.md

---

### Limpieza

- NO ensuciar root
- Usar solo /tmp y /docs
- Mantener estructura limpia

---

## 🧩 REGLA DE ENTREGA DE CÓDIGO

- NO dar instrucciones manuales de edición
- SIEMPRE usar:

  cat > archivo << 'EOF'

- Entregar ficheros completos
- NO parches parciales

---

## 🔄 FLUJO DE SESIÓN

### 0. OUTBRIEFING (OBLIGATORIO)

Antes de cerrar sesión:

Debe responder:

- ¿Dónde estamos?
- ¿Qué hemos entendido?
- ¿Qué decisión se ha tomado?
- ¿Hacia dónde vamos?
- ¿Qué NO vamos a hacer?

Formato:

# OUTBRIEFING

## Estado actual
...

## Lo que hemos entendido hoy
...

## Decisión clave
...

## Hacia dónde vamos ahora
...

## Qué NO vamos a hacer
...

## Intención de la siguiente fase
...

---

### 1. DOCUMENTOS DE CONTINUIDAD

Generar siempre:

- docs/ROADMAP.md
- docs/CHANGELOG.md
- docs/HANDOFF_CURRENT.md
- docs/NEXT_SESSION.md
- docs/SESSION_LOG_YYYY_MM_DD.md

Formato obligatorio:
cat > archivo << 'MD'

---

### 2. CONSISTENCIA

Validar coherencia entre:

- roadmap
- next session
- handoff
- changelog

---

### 3. COMMIT

Formato:

git commit -m "mensaje claro y estratégico"

---

### 4. PROMPT SIGUIENTE SESIÓN

Debe incluir:

- contexto real
- estado actual
- objetivo
- reglas (NO asumir, NO refactor ciego, etc.)

---

## 🎯 PRINCIPIO RECTOR

**Primero control. Luego expansión.**

