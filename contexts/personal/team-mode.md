---
context: personal
name: Modo Equipo
description: Más formal, PR templates, commit messages descriptivos, revisión estricta
---

## Modo Equipo Activo

### Cambios en el proceso
- Commits con scope: `feat(auth): add JWT refresh endpoint`
- PR description completa: contexto, cambios, testing, screenshots si aplica
- Revisión de código más estricta: buscar impacto en otros componentes
- Cambios en contratos (API, schemas) requieren coordinación

### Comunicación
- Comentarios de código más explicativos (otro desarrollador va a leer esto)
- Nombres de variables y funciones más descriptivos
- Documentar asunciones no obvias

### No hacer
- Force push a ramas compartidas
- Merge sin CI verde
- Cambios de breaking changes sin deprecation notice

### Artefactos extras
- CHANGELOG.md actualizado para releases
- Migration guide si hay breaking changes
