---
context: stack
name: Python · FastAPI
description: FastAPI 0.115+ · Python 3.12+ · Pydantic v2 · async-first
---

## Stack Python/FastAPI

### Patterns obligatorios
- Async por defecto en todos los endpoints (`async def`)
- Pydantic v2 para todos los schemas — nunca dicts raw
- Dependency injection para DB sessions, auth, settings
- Repository pattern para acceso a datos
- `BaseSettings` para configuración — nunca hardcoded

### Estructura de proyecto
```
src/
├── api/routers/       ← un router por dominio
├── core/config.py     ← BaseSettings
├── domain/            ← models + schemas por dominio
├── repositories/      ← acceso a datos
├── services/          ← lógica de negocio
└── tests/             ← espejo de src/
```

### Prohibido
- `import *`
- Lógica de negocio en routers
- DB calls directos sin repository
- Secrets en código

### Testing
- pytest + httpx AsyncClient para endpoints
- pytest-asyncio para tests async
- Fixtures en conftest.py — no repetir setup
