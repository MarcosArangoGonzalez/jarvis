---
context: stack
name: Docker · Docker Compose
description: Multi-stage builds · Compose para dev · healthchecks obligatorios
---

## Stack Docker/Compose

### Dockerfile
- Multi-stage siempre: `builder` → `runtime`
- Runtime mínimo: `python:3.12-slim`, `eclipse-temurin:21-jre`, `node:22-alpine`
- `.dockerignore` estricto: excluir `.git`, `node_modules`, `*.pyc`, `__pycache__`
- `HEALTHCHECK` en todos los servicios
- No ejecutar como root: `USER nonroot`

### Docker Compose (dev)
```yaml
services:
  app:
    build: .
    environment:
      - ENV=development
    volumes:
      - ./src:/app/src  # hot reload
    depends_on:
      db:
        condition: service_healthy
  db:
    image: postgres:16-alpine
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
```

### Prohibido
- `latest` como tag en producción
- Secrets como variables de entorno hardcoded (usar secretos de Docker/Bitwarden)
- Volúmenes sin healthcheck en dependencias críticas
