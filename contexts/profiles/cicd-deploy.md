---
context: profiles
name: CI/CD y Deployment
description: Perfil para trabajo con pipelines, Docker y despliegues
---

## Perfil: CI/CD y Deployment

**Activa:** sonnet-default + docker-compose + cicd + deployment + security

**MCP activos:** github + sonar (si disponible)

**Pre-checks obligatorios:**
1. Security scanner sin hallazgos HIGH
2. Quality gate de SonarQube verde
3. Tests pasan en local antes de push

**Reglas de sesión:**
- Confirmar antes de cualquier deploy a producción
- Documentar rollback plan antes del deploy
- Verificar healthchecks post-deploy
- Registrar deploy en vault/01-Projects/

**Comandos clave:**
- Ver estado CI: `/dev_hub` → panel CI/CD
- Trigger deploy preview: `POST /api/cicd/trigger`
