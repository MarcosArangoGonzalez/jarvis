---
name: bitwarden
type: skill
description: Accede a la bóveda de Bitwarden para recuperar credenciales y gestionar secretos de proyectos.
status: configured
---

# Bitwarden Skill

Gestión de secretos con Bitwarden CLI + MCP oficial.

## Setup

```bash
bw login
export BW_SESSION=$(bw unlock --raw)
# Añadir BW_SESSION a .env (gitignored)
```

## Convención de nombres

```
proyecto/entorno/servicio
jarvis/prod/postgresql
jarvis/dev/openai-key
tfg/staging/github-token
```

## Operaciones disponibles

```bash
# Recuperar credencial
bw get item "jarvis/dev/perplexity-key"

# Generar password seguro
bw generate -luns 32

# Crear nueva entrada
bw create item

# Buscar en bóveda
bw list items --search jarvis
```

## MCP (si configurado)

El servidor MCP oficial de Bitwarden permite recuperar secretos directamente
desde Claude Code sin exponer el BW_SESSION en la terminal.

Repo: https://github.com/bitwarden/mcp-server

## Reglas de seguridad

- NUNCA imprimir el valor de un secreto en output visible
- NUNCA hardcodear secretos en código
- SIEMPRE exportar como variable de entorno
- ROTAR secrets comprometidos inmediatamente
