---
title: "SIE Practica 3 Odoo - Plan de Implementacion"
type: plan
status: active
tags:
  - sie
  - odoo
  - implementation
created: 2026-04-20
updated: 2026-04-20
sources:
  - "/home/marcos/jarvis/wiki/projects/sie/odoo-practica3/spec.md"
Summary: "Plan tecnico para implementar el modulo de audiolibros en Odoo 19."
---

# Plan de Implementacion

## Modulo

Nombre tecnico: `sie_audiobook_library`.

El modulo se instala en Odoo 19 dentro de `/home/marcos/Escritorio/odoo/addons/19.0`.

## Modelos

- `sie.audiobook`: entidad principal del catalogo.
- `sie.audiobook.author`: autores de audiolibros.
- `sie.audiobook.producer`: productores/editoriales.
- `sie.audiobook.genre`: generos.
- `sie.audiobook.format`: formatos.

## Relaciones

- Un audiolibro puede tener varios autores: `Many2many`.
- Un audiolibro tiene un productor: `Many2one`.
- Un audiolibro tiene un genero: `Many2one`.
- Un audiolibro tiene un formato: `Many2one`.

## Seguridad

Crear categoria `Audiobook Library`, privilegio `Audiobook Library` y grupo `Audiobook Library / User` con el modelo `res.groups.privilege` de Odoo 19. Los permisos CRUD se definen sobre todos los modelos del modulo mediante `ir.model.access.csv`.

## Compatibilidad Odoo 19

- Usar `models.Constraint` en lugar de `_sql_constraints`.
- Montar addons externos en `/mnt/extra-addons` mediante `compose.override.yml`.
- Incluir `/mnt/extra-addons` en `addons_path`.

## Vistas y Navegacion

- Menu raiz: `Audiolibros`.
- Submenu `Catalogo > Audiolibros`.
- Submenu `Configuracion` para autores, productores, generos y formatos.
- Vista lista, formulario, busqueda y kanban para audiolibros.
- Vista lista/formulario para modelos auxiliares.

## Criterios de Aceptacion

- El modulo aparece en Apps y se instala sin errores.
- El menu `Audiolibros` aparece tras la instalacion.
- Se pueden crear, leer, modificar y borrar audiolibros.
- Las relaciones permiten mantener autores, productor, genero y formato.
- El ISBN se valida como unico.
- El precio no puede ser negativo.
- La duracion no puede ser negativa.
