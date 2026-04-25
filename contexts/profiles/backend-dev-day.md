---
context: profiles
name: Backend Dev — día normal
description: Perfil completo para día de implementación backend con Python/FastAPI
---

## Perfil: Backend Dev — día normal

**Activa:** sonnet-default + python-fastapi + implementation + security + solo-mode

**MCP activos:** context7 + github

**Hooks:** wiki-lint + session log al cerrar

**Reglas de sesión:**
- Leer contexto del vault antes de modificar código existente
- Security scanner antes de cada commit
- Actualizar jarvis-log.md al cerrar si hubo cambios significativos

**Objetivo típico:** implementar features, corregir bugs, añadir tests en el stack FastAPI/Python.
