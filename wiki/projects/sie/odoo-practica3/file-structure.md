---
title: "SIE Practica 3 Odoo - Estructura de Ficheros"
type: reference
status: active
tags:
  - sie
  - odoo
  - files
created: 2026-04-20
updated: 2026-04-20
sources:
  - "/home/marcos/jarvis/odoo_modules/sie_audiobook_library"
Summary: "Estructura esperada del modulo Odoo de audiolibros."
---

# Estructura de Ficheros

```text
sie_audiobook_library/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── audiobook.py
│   ├── audiobook_author.py
│   ├── audiobook_format.py
│   ├── audiobook_genre.py
│   └── audiobook_producer.py
├── security/
│   ├── audiobook_security.xml
│   └── ir.model.access.csv
├── views/
│   ├── audiobook_author_views.xml
│   ├── audiobook_format_views.xml
│   ├── audiobook_genre_views.xml
│   ├── audiobook_producer_views.xml
│   ├── audiobook_views.xml
│   └── menu_views.xml
├── data/
│   └── demo_data.xml
├── static/
│   └── description/
└── README.md
```

## Ficheros Python

- `__manifest__.py`: metadatos, dependencias y carga de XML/CSV.
- `models/audiobook.py`: modelo principal, restricciones y campos del catalogo.
- `models/audiobook_author.py`: autores.
- `models/audiobook_producer.py`: productores.
- `models/audiobook_genre.py`: generos.
- `models/audiobook_format.py`: formatos.

## Ficheros de Documentacion

- `README.md`: resumen del modulo, instalacion y uso.
- `wiki/projects/sie/odoo-practica3/*.md`: documentacion Jarvis del proyecto, plan, pruebas y entrega.
- Memoria opcional: crear en `/home/marcos/Escritorio/SIE/borradores/` o incluir como PDF junto al ZIP si se redacta.

