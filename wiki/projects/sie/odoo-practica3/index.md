---
title: "SIE - Practica 3 Odoo"
type: project
status: active
tags:
  - sie
  - odoo
  - practica
  - universidad
created: 2026-04-20
updated: 2026-04-20
tokens_consumed: 0
sources:
  - "/home/marcos/Descargas/SIE-P3.Odoo-Modulo.pdf"
  - "/home/marcos/Escritorio/odoo"
Summary: "Practica 3 de SIE: modulo Odoo para gestionar una biblioteca de audiolibros."
---

# SIE - Practica 3 Odoo

## Objetivo

Desarrollar un modulo Odoo para que una empresa dedicada a la venta de audiolibros pueda gestionar su catalogo.

El modulo debe permitir visualizar, introducir, modificar y borrar audiolibros, manteniendo informacion sobre autores, titulo, productor, duracion, portada, genero, formato, ISBN y precio.

## Entrega

| Campo | Valor |
|---|---|
| Fecha limite | 15 de mayo de 2026 |
| Entrega | Actividad "Practica 3 Odoo - Modulo" en campus virtual UDC |
| Formato | Un unico comprimido `.zip`, `.rar`, etc. |
| Nombre | `practica3_<apellido1>_<apellido2>_<nombre>.<extension>` |
| Contenido | Codigo del modulo Odoo comentado adecuadamente |
| Memoria | Opcional, PDF de maximo 2 paginas |

## Entorno Local

| Recurso | Ubicacion |
|---|---|
| Odoo compose | `/home/marcos/Escritorio/odoo/compose.yml` |
| Odoo override staging | `/home/marcos/jarvis/odoo_config/compose.override.yml` |
| Odoo config staging | `/home/marcos/jarvis/odoo_config/odoo.conf` |
| Odoo override final | `/home/marcos/Escritorio/odoo/compose.override.yml` |
| Odoo config final | `/home/marcos/Escritorio/odoo/odoo.conf` |
| Addons Odoo 19 | `/home/marcos/Escritorio/odoo/addons/19.0` |
| Modulo Jarvis staging | `/home/marcos/jarvis/odoo_modules/sie_audiobook_library` |
| Modulo Odoo final | `/home/marcos/Escritorio/odoo/addons/19.0/sie_audiobook_library` |

## Documentacion

- [[spec]]: requisitos extraidos del PDF.
- [[implementation-plan]]: diseno tecnico.
- [[file-structure]]: estructura de ficheros.
- [[test-plan]]: pruebas y checklist.
- [[delivery]]: preparacion del comprimido final.
