---
context: workflow
name: Planificación
description: Fase de diseño: ADRs, diagramas, definición de alcance
---

## Modo Planificación

### Antes de implementar cualquier feature
1. Definir el problema en una frase
2. Listar alternativas (mínimo 2)
3. Documentar la decisión en un ADR si afecta a >1 componente
4. Crear diagrama de arquitectura (Mermaid) para sistemas nuevos
5. Estimar esfuerzo: S (<2h), M (<1d), L (<3d), XL (>3d)

### Formato ADR
```markdown
# ADR-NNN: Título

## Contexto
[Por qué se toma esta decisión]

## Decisión
[Qué se decide hacer]

## Consecuencias
[Trade-offs aceptados]
```

### Guardar en
`vault/01-Projects/<proyecto>/adrs/ADR-NNN-titulo.md`

### No implementar sin
- Alcance definido
- Criterios de aceptación claros
- Impacto en componentes existentes evaluado
