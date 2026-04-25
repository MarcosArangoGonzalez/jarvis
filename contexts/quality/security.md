---
context: quality
name: Seguridad
description: OWASP Top 10, secrets, auth, input validation — siempre activo
---

## Contexto de Seguridad

### Reglas siempre activas
- OWASP Top 10 como constraint implícita en todo código generado
- Nunca hardcoded: API keys, passwords, tokens, certificados
- Input validation en toda frontera de sistema (user input, external APIs)
- SQL: siempre parameterized queries — nunca f-strings o concatenación
- Auth: JWT con RS256, expiración corta, refresh tokens, revocación

### Pre-commit
El hook de seguridad detecta automáticamente:
- AWS keys, JWT tokens secretos
- Passwords y API keys en formato estándar
- Base64 sospechoso (posibles secretos codificados)

### Durante code review
- Verificar que todos los secrets vienen de variables de entorno
- Confirmar que no hay logging de datos sensibles
- Revisar permisos de archivos en Dockerfile

### Severidad de hallazgos
- HIGH: bloquea merge — corregir inmediatamente
- WARNING: documentar o corregir antes de release
- INFO: registrar para revisión posterior
