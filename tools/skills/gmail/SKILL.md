---
name: gmail
description: Busca y extrae emails/newsletters de Gmail para JarvisOS cuando OAuth esté configurado. Úsala para revisar emails, buscar newsletters recibidas o extraer contenido hacia el vault.
---

# Gmail

## Scripts

- `python3 tools/skills/gmail/search_gmail.py "<query>" --max 20`
- `python3 tools/skills/gmail/read_email.py <message_id>`
- `python3 tools/skills/gmail/extract_newsletter.py <message_id>`

Los scripts devuelven error controlado si no existe `~/.gmail-mcp/gcp-oauth.keys.json`.
