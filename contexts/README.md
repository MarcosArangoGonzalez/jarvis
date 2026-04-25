# Sistema de Contextos Cargables

Los archivos de esta carpeta son fragmentos de CLAUDE.md que el Session Wizard
concatena para generar el contexto exacto de cada sesión de trabajo.

## Estructura

```
contexts/
├── models/      → selector de modelo IA
├── stack/       → tecnologías y frameworks
├── workflow/    → fase del proceso de software
├── quality/     → estándares de calidad
├── personal/    → modo de trabajo personal
└── profiles/    → combinaciones predefinidas
```

## Uso

1. En `/session/new` del dashboard → seleccionar dimensiones
2. El wizard concatena los .md seleccionados
3. Se genera un CLAUDE.md de sesión optimizado
4. El perfil se guarda en `vault/04-Skills/contexts/`

## Formato de cada archivo

```yaml
---
context: <categoría>
name: <nombre legible>
description: <una línea>
---
# Contenido del contexto
```
