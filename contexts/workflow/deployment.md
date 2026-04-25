---
context: workflow
name: Deployment
description: Fase de despliegue: Docker, Vercel, cloud, healthchecks
---

## Modo Deployment

### Checklist pre-deploy
- [ ] Todos los tests pasan en CI
- [ ] Quality gate de SonarQube verde
- [ ] Security scan sin hallazgos HIGH
- [ ] Variables de entorno configuradas en destino (no en código)
- [ ] Rollback plan definido

### Estrategias por entorno
- **Preview**: deploy automático en cada PR (Vercel/staging)
- **Producción**: merge a main → pipeline CI → confirmación manual
- **Rollback**: `git revert` + redeploy, o rollback de imagen Docker

### Healthchecks obligatorios
Todos los servicios deben exponer `/health` o `/healthz`:
```json
{"status": "healthy", "version": "1.2.3", "timestamp": "..."}
```

### Post-deploy
- Verificar healthcheck en destino
- Monitorear logs durante 5 minutos
- Registrar deploy en vault/01-Projects/
