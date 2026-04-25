---
context: workflow
name: Code Review
description: Fase de revisión: seguridad, calidad, arquitectura
---

## Modo Code Review

### Orden de revisión
1. **Seguridad** — OWASP Top 10, secrets, injection, auth
2. **Corrección** — lógica, edge cases, error handling
3. **Arquitectura** — acoplamiento, cohesión, principios SOLID
4. **Tests** — cobertura, calidad de fixtures, casos límite
5. **Legibilidad** — nombres, estructura, comentarios útiles

### Severidad de hallazgos
- 🔴 BLOCKER: problema de seguridad o lógica crítica → no mergear
- 🟡 MAJOR: deuda técnica significativa → resolver antes de release
- 🟢 MINOR: mejora opcional → puede ir en ticket separado

### Formato de feedback
```
[BLOCKER/MAJOR/MINOR] archivo:línea
Descripción del problema.
Sugerencia: ...
```

### Herramientas
- SonarQube: quality gate debe pasar antes de merge
- Security scanner: 0 hallazgos HIGH antes de merge
