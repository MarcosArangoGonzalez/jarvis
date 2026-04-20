---
title: "SIE Tasks"
type: tasks
status: active
tags:
  - sie
  - investigacion
  - presentacion
  - odoo
  - tasks
created: 2026-04-13
updated: 2026-04-20
tokens_consumed: 0
sources:
  - "/home/marcos/jarvis/wiki/projects/sie.md"
Summary: "Lista de tareas del trabajo de investigación SIE: investigación, redacción y presentación."
---

# SIE Tasks

## Active Queue

### Practica 3 Odoo

| Priority | Task | Feature | Status | Conclusion | Next Action |
|---|---|---|---|---|---|
| P0 | Copiar modulo a addons Odoo | Odoo | Done | Modulo copiado a `/home/marcos/Escritorio/odoo/addons/19.0/sie_audiobook_library`. | Mantener staging y copia real sincronizados si se hacen cambios. |
| P0 | Instalar modulo en Odoo | Odoo | Backlog | Hay entorno Docker Odoo 19 en `/home/marcos/Escritorio/odoo`. | Levantar Odoo, actualizar Apps e instalar `SIE Audiobook Library`. |
| P1 | Validar CRUD de audiolibros | Testing | Backlog | El enunciado exige visualizar, introducir, modificar y borrar. | Ejecutar checklist de `wiki/projects/sie/odoo-practica3/test-plan.md`. |
| P1 | Validar reglas y relaciones | Testing | Backlog | ISBN unico, precio/duracion no negativos, relaciones de autores/productor/genero/formato. | Crear registros demo y probar validaciones. |
| P2 | Redactar memoria opcional | Documentacion | Backlog | El PDF permite memoria de maximo 2 paginas. | Decidir si se entrega memoria y redactarla en `SIE/borradores/`. |
| P2 | Preparar ZIP final | Entrega | Backlog | Entrega antes del 15/05/2026. | Confirmar nombre de pareja y comprimir modulo segun `delivery.md`. |

### Trabajo Tutelado / Investigacion

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

## Dependencias Practica 3 Odoo

1. Copia del modulo al directorio de addons.
2. Instalacion en Odoo.
3. Pruebas CRUD y validaciones.
4. Confirmacion del nombre final de entrega.
5. Generacion del comprimido final.
