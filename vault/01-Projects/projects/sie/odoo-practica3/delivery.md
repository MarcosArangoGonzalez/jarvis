---
title: "SIE Practica 3 Odoo - Entrega"
type: delivery
status: active
tags:
  - sie
  - odoo
  - entrega
created: 2026-04-20
updated: 2026-04-20
sources:
  - "/home/marcos/Descargas/SIE-P3.Odoo-Modulo.pdf"
Summary: "Notas para preparar el comprimido final de la practica 3."
tokens_consumed: 84
---

# Entrega

## Comprimido

Formato exigido:

```text
practica3_<apellido1>_<apellido2>_<nombre>.<extension>
```

Nombre probable si la entrega es individual:

```text
practica3_Arango_Gonzalez_Marcos.zip
```

Confirmar antes de entregar si debe incluir tambien los apellidos/nombre de la pareja.

## Contenido

El comprimido debe incluir:

```text
sie_audiobook_library/
```

Opcionalmente puede incluir:

```text
memoria_practica3.pdf
```

## Comando Sugerido

Desde `/home/marcos/Escritorio/odoo/addons/19.0`:

```bash
zip -r practica3_Arango_Gonzalez_Marcos.zip sie_audiobook_library \
  -x '*/__pycache__/*' '*.pyc' '*/.DS_Store'
```

