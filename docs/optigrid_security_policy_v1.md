# Política de seguridad por modos de despliegue — OptiGrid CRM

## 1. Objetivo

Definir cómo varían las reglas de identidad, asociación, ownership y administración de entidades según el contexto de despliegue del sistema.

---

## 2. Principios base

### Identidad no equivale a ownership
Autenticarse con un email válido demuestra quién es el usuario, pero no demuestra que controle una empresa.

### Afiliación no equivale a control
Pertenecer a un dominio puede sugerir relación, pero no prueba control.

### Cambios sensibles requieren validación
Las acciones críticas deben pasar por reglas explícitas y ser auditables.

### Trazabilidad obligatoria
Todo cambio relevante debe generar eventos.

---

## 3. Modos de despliegue

### private_local
- entorno controlado
- un único administrador
- sin riesgo externo real

### public
- acceso abierto
- usuarios externos
- riesgo de suplantación y abuso

---

## 4. Conceptos clave

- Identidad: quién es el usuario
- Asociación: relación con empresa
- Ownership: control administrativo
- Administración: capacidad de gestión

---

## 5. Regla maestra

Email = identidad  
Dominio = posible afiliación  
Ownership = verificación explícita

---

## 6. Política por modo

### private_local
- simplificación de reglas
- ownership asignado manualmente
- sin verificación obligatoria

### public
- ownership nunca automático
- verificación obligatoria
- roles explícitos
- auditoría completa

---

## 7. Dominios

### Corporativos
- permiten inferir afiliación
- no permiten ownership automático

### Genéricos
- solo identifican buzón
- no permiten crear empresa por dominio

---

## 8. Ownership

- no automático
- requiere verificación o asignación
- siempre auditable

---

## 9. Verificación de dominio

Estados:
- unverified
- pending
- verified
- rejected

Métodos:
- DNS TXT (recomendado)
- archivo web
- validación manual

---

## 10. Roles

- external
- member
- admin
- owner

Nunca asignados automáticamente en modo public.

---

## 11. CRM Update Engine

No debe:
- asignar ownership automáticamente
- escalar permisos

Debe:
- proponer
- registrar
- esperar aprobación

---

## 12. Eventos

- company_claim_requested
- company_claim_approved
- company_claim_rejected
- domain_verification_completed

---

## 13. Compatibilidad futura

El modelo completo siempre existe.  
Solo cambia el nivel de enforcement.

---

## 14. Resumen

- privado → confianza por perímetro
- público → confianza por verificación
- email ≠ ownership
- dominio ≠ control
- ownership = decisión explícita
