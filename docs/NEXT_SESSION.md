# NEXT SESSION

## Estado actual

Pipeline IA-first completamente operativo.

EmailMessage  
→ FactRecord  
→ InferenceRecord  
→ CRMUpdateProposal  
→ AIRecommendation

Demo funcional mediante:

python manage.py demo_email_flow

---

# Objetivo de la próxima sesión

Crear interfaz de inspección del pipeline.

---

# Tareas

## 1 Crear vista de emails procesados

URL:

/emails/

Mostrar:

- email_id
- subject
- sender
- facts count
- inferences count
- proposals count
- recommendations count

---

## 2 Crear vista de detalle

URL:

/emails/<id>/

Mostrar:

EmailMessage  
Facts  
Inferences  
Proposals  
Recommendations

---

## 3 Añadir navegación mínima

Template simple Django.

---

# Objetivo

Poder visualizar el "cerebro del CRM".

