---
title: "SIE Tasks"
type: tasks
status: active
tags:
  - sie
  - investigacion
  - presentacion
  - tasks
created: 2026-04-13
updated: 2026-04-13
tokens_consumed: 0
sources:
  - "/home/marcos/jarvis/wiki/projects/sie.md"
Summary: "Lista de tareas del trabajo de investigación SIE: investigación, redacción y presentación."
---

# SIE Tasks

## Active Queue

| Priority | Task | Feature | Status | Conclusion | Next Action |
|---|---|---|---|---|---|
| P0 | Configurar OAuth Google Drive MCP | Integración | Pendiente | Sin credenciales el MCP gdrive no funciona. | Ejecutar flujo OAuth de `@modelcontextprotocol/server-gdrive`. |
| P1 | Revisar doc principal en Drive | Investigación | Backlog | Saber qué está redactado y qué falta. | Leer secciones actuales e identificar gaps. |
| P1 | Ampliar investigación | Investigación | WIP | Hay fuentes en NotebookLM; necesita más contenido. | Identificar subtemas sin cubrir y buscar fuentes. |
| P1 | Redactar contenido pendiente | Redacción | Backlog | El doc necesita más desarrollo. | Definir secciones vacías y asignar orden de redacción. |
| P2 | Diseñar estructura de la presentación | Presentación | Backlog | Depende del contenido redactado. | Crear outline de slides en `SIE/presentacion/`. |
| P2 | Desarrollar slides | Presentación | Backlog | Contenido visual y narrativa de presentación. | Implementar tras tener el borrador escrito. |

## Dependencias

1. OAuth Google Drive → acceso al doc desde Jarvis/Claude
2. Revisión del doc → saber qué queda por redactar
3. Investigación → redacción → presentación
