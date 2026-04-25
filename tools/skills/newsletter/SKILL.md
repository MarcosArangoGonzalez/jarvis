---
name: newsletter
description: Genera el newsletter diario de JarvisOS desde vault, RSS/Gmail configurables y fuentes locales. Úsala ante solicitudes como "genera el newsletter", "daily news", "resumen del día" o "qué hay de nuevo hoy".
---

# Newsletter

## Comando principal

```bash
python3 tools/skills/newsletter/newsletter_engine.py --date today --output html,md,pdf
```

## Opciones

- `--sections tech,bjj`: limita secciones.
- `--no-pdf`: genera solo Markdown + HTML.
- `--check`: verifica rutas y dependencias opcionales.

## Salida

Guarda artefactos en `vault/00-Daily/newsletters/YYYY-MM-DD.{md,html,pdf}`.
PDF solo se crea si `weasyprint` está instalado.
