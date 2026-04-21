---
title: "SIE Log"
type: log
status: active
tags:
  - sie
  - log
  - universidad
created: 2026-04-21
updated: 2026-04-21
tokens_consumed: 0
sources:
  - "/home/marcos/jarvis/wiki/projects/sie.md"
  - "/home/marcos/Descargas/SIE-P3.Odoo-Modulo.pdf"
Summary: "Log centralizado del trabajo de SIE: investigacion y Practica 3 Odoo."
---

# SIE Log

## 2026-04-13 — Bootstrap del espacio SIE

- Directorio local creado en `/home/marcos/Escritorio/SIE` con estructura base para `pdfs/`, `investigacion/`, `presentacion/`, `borradores/` y `notas/`.
- MCP filesystem `sie-filesystem` anadido para apuntar al directorio local del proyecto.
- MCP Google Drive registrado; queda pendiente completar el flujo OAuth.
- NotebookLM ya estaba conectado al documento principal de Drive y a los PDFs/investigaciones del trabajo tutelado.

## 2026-04-20 — Practica 3 Odoo: implementacion del modulo

- Leido `/home/marcos/Descargas/SIE-P3.Odoo-Modulo.pdf` y separado el alcance de la practica respecto al trabajo tutelado.
- Creado apartado especifico en Jarvis bajo `wiki/projects/sie/odoo-practica3/` con especificacion, plan tecnico, estructura de ficheros, pruebas y entrega.
- Implementado modulo `sie_audiobook_library` en staging `odoo_modules/sie_audiobook_library/` con:
  - modelos Python para audiolibros, autores, productores, generos y formatos;
  - seguridad y permisos CRUD;
  - vistas, menus, search y datos demo;
  - README tecnico para instalacion y uso.
- Copiado el modulo al addon real: `/home/marcos/Escritorio/odoo/addons/19.0/sie_audiobook_library`.

## 2026-04-20 — Ajustes del entorno Odoo 19

- Detectado que el `compose.yml` local montaba `./addons` en `/var/lib/odoo/addons/19.0`, dejando el addon un nivel por debajo del esperado.
- Creado `odoo.conf` y `compose.override.yml` para montar `./addons/19.0` en `/mnt/extra-addons` y anadirlo a `addons_path`.
- Dejado el entorno Odoo operativo en `http://localhost:8069`.

## 2026-04-20 — Validacion tecnica del modulo

- Primer intento de instalacion CLI en `sie_p3_test` detecto incompatibilidad Odoo 19 en seguridad: `res.groups.category_id` ya no existe.
- Adaptada la seguridad a `res.groups.privilege`.
- Sustituidas restricciones `_sql_constraints` por `models.Constraint`.
- Segundo intento de instalacion en `sie_p3_test2` detecto incompatibilidad en la search view; la vista se reescribio a sintaxis valida de Odoo 19.
- Instalacion final validada en base limpia `sie_p3_test3`.
- Verificado en base de datos que `sie_audiobook_library` queda en estado `installed`.
- Eliminadas las bases temporales fallidas `sie_p3_test` y `sie_p3_test2`.

## 2026-04-21 — Centralizacion de logs

- Reorganizados los logs para que el seguimiento de SIE viva en `wiki/logs/projects/sie-log.md`.
- La nota de proyecto SIE queda como punto de entrada y resumen, no como historial largo.

## Siguiente accion

- Ejecutar validacion manual desde UI en `http://localhost:8069` usando la base `sie_p3_test3`.
- Comprobar CRUD, relaciones y validaciones desde formulario.
- Confirmar nombre final de pareja y generar el ZIP de entrega.

