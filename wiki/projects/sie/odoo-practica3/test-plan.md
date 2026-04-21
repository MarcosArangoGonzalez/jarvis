---
title: "SIE Practica 3 Odoo - Test Plan"
type: test-plan
status: active
tags:
  - sie
  - odoo
  - testing
created: 2026-04-20
updated: 2026-04-20
sources:
  - "/home/marcos/jarvis/wiki/projects/sie/odoo-practica3/implementation-plan.md"
Summary: "Checklist de validacion del modulo Odoo de audiolibros."
---

# Test Plan

## Preparacion

1. Ir a `/home/marcos/Escritorio/odoo`.
2. Levantar Odoo con `docker compose up -d`.
3. Abrir `http://localhost:8069`.
4. Confirmar que `/home/marcos/Escritorio/odoo/odoo.conf` contiene `/mnt/extra-addons` en `addons_path`.
5. Activar modo desarrollador si es necesario.
6. Actualizar lista de aplicaciones.
7. Instalar `SIE Audiobook Library`.

## Pruebas Funcionales

- Verificar que aparece el menu `Audiolibros`.
- Crear autores, productor, genero y formato.
- Crear un audiolibro con todos los campos obligatorios.
- Anadir portada al audiolibro.
- Editar titulo, precio, duracion, genero y formato.
- Asociar varios autores al mismo audiolibro.
- Borrar un audiolibro de prueba.
- Buscar por titulo, ISBN, autor, productor, genero y formato.
- Agrupar por genero, formato y productor.

## Pruebas de Validacion

- Intentar crear un audiolibro con ISBN duplicado: debe fallar.
- Intentar guardar precio negativo: debe fallar.
- Intentar guardar duracion negativa: debe fallar.

## Checklist de Entrega

- El modulo se instala desde una base limpia.
- El codigo incluye comentarios utiles, no ruido.
- El ZIP contiene la carpeta `sie_audiobook_library`.
- El ZIP no contiene caches Python ni archivos temporales.
- El nombre del ZIP sigue el formato pedido por el PDF.
- Si se anade memoria, no supera dos paginas.
