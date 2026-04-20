---
title: "SIE - Trabajo de Investigación"
type: project
status: active
tags:
  - sie
  - investigacion
  - presentacion
  - odoo
  - universidad
created: 2026-04-13
updated: 2026-04-20
tokens_consumed: 0
sources:
  - "https://docs.google.com/document/d/1UL570oHD5F6zx-q6utapLoqkyNb7ZuDhKjRIhtGKSc8/edit"
  - "/home/marcos/Escritorio/SIE"
  - "/home/marcos/Descargas/SIE-P3.Odoo-Modulo.pdf"
Summary: "Trabajo de investigación SIE con presentación. Docs en Google Drive y fuentes en NotebookLM. Directorio local en ~/Escritorio/SIE."
---

# SIE - Trabajo de Investigación

## Apartados

- [[odoo-practica3/index|Practica 3 Odoo - Modulo de Audiolibros]]
- Trabajo tutelado / investigacion: se mantiene en este documento y en `wiki/tasks/projects/sie.md`.

## Objetivo

Trabajo de investigación que requiere:
- Continuar investigando y recopilar fuentes
- Redactar contenido del trabajo escrito
- Preparar y desarrollar la presentación

## Recursos

| Recurso | Ubicación | Estado |
|---|---|---|
| Documento principal | [Google Drive](https://docs.google.com/document/d/1UL570oHD5F6zx-q6utapLoqkyNb7ZuDhKjRIhtGKSc8/edit) | Activo |
| Fuentes y PDFs | NotebookLM (conectado al doc de Drive + PDFs de clase + investigaciones) | Activo |
| Directorio local | `/home/marcos/Escritorio/SIE` | Configurado |

## Estructura local

```
SIE/
├── pdfs/           # PDFs de clase y artículos
├── investigacion/  # Notas y fuentes de investigación
├── presentacion/   # Slides y materiales de presentación
├── borradores/     # Versiones de trabajo del escrito
└── notas/          # Apuntes de sesión y decisiones
```

## Integración MCP

- `sie-filesystem`: MCP filesystem apuntando a `/home/marcos/Escritorio/SIE`
- `google-drive`: MCP Google Drive (requiere OAuth — ver estado de credenciales)

## Estado de credenciales Google

- Credenciales OAuth esperadas en: `~/.config/jarvis/gdrive_credentials.json`
- Estado: **pendiente de configurar**
- Para activar: ejecutar el flujo OAuth de `@modelcontextprotocol/server-gdrive`

## Log de sesiones

### 2026-04-20
- Leido `/home/marcos/Descargas/SIE-P3.Odoo-Modulo.pdf`.
- Detectado entorno Odoo local en `/home/marcos/Escritorio/odoo` con addons en `/home/marcos/Escritorio/odoo/addons/19.0`.
- Creado nuevo apartado Jarvis para la Practica 3 Odoo en `wiki/projects/sie/odoo-practica3/`.
- Preparado modulo `sie_audiobook_library` en staging Jarvis: `odoo_modules/sie_audiobook_library/`.
- Copiado el modulo al directorio real de addons: `/home/marcos/Escritorio/odoo/addons/19.0/sie_audiobook_library`.
- Siguiente accion: instalarlo en Odoo y ejecutar el checklist de pruebas.

### 2026-04-13
- Directorio local creado con estructura inicial.
- MCP filesystem (`sie-filesystem`) añadido a `~/.claude/settings.json`.
- MCP Google Drive (`google-drive`) registrado — pendiente de OAuth.
- Nota de proyecto creada en wiki Jarvis.
- NotebookLM ya conectado al doc de Drive + PDFs + investigaciones.
