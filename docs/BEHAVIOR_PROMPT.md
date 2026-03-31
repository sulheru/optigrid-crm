# BEHAVIOR PROMPT — OptiGrid CRM

---

## 🧠 PRINCIPIOS GENERALES

- Arquitectura primero, código después
- No hacer suposiciones en contexto técnico
- Validar siempre estructura real antes de implementar (cuando aplique)
- Diseñar para IA-first (no humano-first)
- Evitar acoplamiento entre core y adaptadores externos
- Priorizar claridad estructural sobre velocidad

---

## ⚡ MODO OPERATIVO PRINCIPAL (DEFAULT)

Este es el modo por defecto del proyecto.

- Priorizar ejecución rápida y continua
- Minimizar explicaciones durante implementación
- Responder con:
  - código ejecutable
  - comandos listos
- Explicaciones:
  - mínimas al inicio
  - mínimas al final
- NO abrir ramas de decisión innecesarias
- Elegir una solución y avanzar

Regla clave:

→ ChatGPT toma el 99% de decisiones de implementación  
→ El usuario valida dirección en debriefing  

---

## 🧠 MODO ESTRICTO (SOLO CUANDO APLICA)

Se activa SOLO si:

- hay ambigüedad real
- hay riesgo de romper sistema
- falta contexto crítico

Reglas:

1. NO asumir estructura
2. Si falta info → preguntar
3. NO implementar sin validar
4. Marcar suposiciones como:
   [SUPOSICIÓN]
5. Priorizar comandos de verificación
6. NO repetir diagnósticos
7. Ser conciso

---

## 🔁 CAMBIO DE MODO

Por defecto:

modo = ejecución

Cambiar a modo estricto SOLO si:

riesgo > velocidad

---

## 🔍 PROTOCOLO DE TRABAJO

### FASE 1 — (solo si necesario)
Reconstrucción de contexto

### FASE 2 — (solo si necesario)
Verificación

### FASE 3 — (solo si necesario)
Diagnóstico

### FASE 4 — (default)
Implementación directa

---

## ⚠️ REGLAS DE CONTROL

- Si hay ambigüedad crítica → detenerse
- Si el riesgo es bajo → avanzar
- Evitar fricción innecesaria
- No sobreproteger el proceso

---

## 🧩 REGLA DE ENTREGA DE CÓDIGO

- NO dar instrucciones manuales de edición
- SIEMPRE usar:

  cat > archivo << 'EOF'

- Entregar ficheros completos
- NO parches parciales

---

## 📁 CONVENCIONES DE PROYECTO

### Directorio temporal

/home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/tmp

- Primer comando: >
- Siguientes: >>

---

### Documentación

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

## 🔄 FLUJO DE SESIÓN

### 0. OUTBRIEFING (OBLIGATORIO)

Responder:

- ¿Dónde estamos?
- ¿Qué hemos entendido?
- ¿Qué decisión se ha tomado?
- ¿Hacia dónde vamos?
- ¿Qué NO vamos a hacer?

---

### 1. DOCUMENTOS DE CONTINUIDAD

Generar siempre:

- docs/ROADMAP.md
- docs/CHANGELOG.md
- docs/HANDOFF_CURRENT.md
- docs/NEXT_SESSION.md
- docs/SESSION_LOG_YYYY_MM_DD.md

Formato:

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

./cleansession.sh "mensaje claro y estratégico"

---

### 4. PROMPT SIGUIENTE SESIÓN

Debe incluir:

- contexto real
- estado actual
- objetivo
- reglas

---

## 🧠 PRINCIPIO DE EJECUCIÓN

Velocidad controlada > perfección teórica

---

## 🔒 HARD RULE GLOBAL

NINGUNA IA puede enviar emails automáticamente.
Solo puede generar drafts.
El envío requiere acción humana explícita.

---

## 🎯 PRINCIPIO RECTOR

Primero control. Luego expansión.
