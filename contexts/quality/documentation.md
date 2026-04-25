---
context: quality
name: Documentación
description: Docstrings mínimos, OpenAPI, README actualizado, vault sync
---

## Contexto de Documentación

### Qué documentar
- APIs públicas: docstring de una línea + tipos
- Decisiones no obvias: comentario con WHY (no WHAT)
- Endpoints: OpenAPI automático via FastAPI/Spring
- Arquitectura: ADRs en vault/01-Projects/

### Qué NO documentar
- Código auto-explicativo (nombres claros bastan)
- Flujos que ya aparecen en el OpenAPI spec
- Funciones privadas simples

### Formato de docstring (Python)
```python
def convert(path: Path) -> IngestionResult:
    """Convert a file in vault inbox to Markdown."""
```

### README mínimo
- Qué hace el proyecto (1 párrafo)
- Cómo ejecutar en local (comandos exactos)
- Variables de entorno requeridas
- Cómo ejecutar tests

### Sincronización con vault
Después de cada feature completada:
- Actualizar `vault/01-Projects/<proyecto>/README.md`
- Si hay decisión arquitectural → crear ADR
