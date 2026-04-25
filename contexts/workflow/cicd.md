---
context: workflow
name: CI/CD
description: Fase de pipeline: GitHub Actions, SonarQube, Docker, deploy
---

## Modo CI/CD

### Pipeline estándar
```
push → lint → test → build → sonar → deploy-preview
                                    ↓ (en main)
                                  deploy-prod
```

### GitHub Actions — jobs obligatorios
- `lint`: ruff/eslint/ktlint según stack
- `test`: pytest/jest/junit con coverage
- `build`: compilar + imagen Docker
- `sonar`: quality gate (cobertura >80%, 0 blockers)
- `security`: dependabot + pip-audit/npm audit

### SonarQube
- Quality gate debe pasar antes de merge a main
- Cobertura mínima: 80%
- 0 issues de severidad Blocker o Critical

### Docker
- Multi-stage build obligatorio
- Imagen base: siempre versión explícita (no `latest`)
- Push a registry solo desde CI — nunca local push a prod

### Comandos rápidos
- Ver estado: `/dev_hub` → panel CI/CD
- Trigger manual: `POST /api/cicd/trigger`
