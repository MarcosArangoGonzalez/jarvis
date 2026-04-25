---
context: workflow
name: Implementación
description: Fase de código: TDD, commits atómicos, sin over-engineering
---

## Modo Implementación

### Reglas de código
- Un commit por cambio lógico — mensajes en imperativo
- Tests junto con el código (TDD cuando sea posible)
- Sin comentarios obvios — solo WHY no-obvio
- Sin abstracciones prematuras: 3 repeticiones antes de extraer
- Sin features no pedidas

### Checklist antes de entregar
- [ ] Tests pasan
- [ ] Sin secretos hardcoded
- [ ] Sin imports sin usar
- [ ] Tipos correctos (no `Any`)
- [ ] Sin `TODO` sin ticket asociado

### No hacer
- Refactors no relacionados con la tarea
- Cambios de formato en archivos no tocados
- Añadir dependencias sin justificación
