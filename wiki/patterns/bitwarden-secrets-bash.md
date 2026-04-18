---
title: "Bitwarden CLI secrets loader (bash)"
type: pattern
status: active
tags:
  - bitwarden
  - secrets
  - bash
  - security
pattern_category: auth
language: bash
complexity: low
reusable: true
created: 2026-04-18
updated: 2026-04-18
tokens_consumed: 180
sources:
  - "tools/skills/../../../toolbox/secrets/load-env.sh"
Summary: "Cargar secretos desde Bitwarden CLI en bash, con fallback a .env. Requiere BW_SESSION activo."
---

# Bitwarden CLI secrets loader (bash)

> Carga API keys desde Bitwarden vault en bash, con fallback a fichero .env si la sesión no está activa.

## Pattern

```bash
# 1. Unlock vault (once per session):
export BW_SESSION=$(bw unlock --raw)

# 2. Load secrets in any script:
source ~/toolbox/secrets/load-env.sh
```

## Key Points

- `bw get password <name>` — recupera valor por nombre de ítem
- `bw get notes <name>` — recupera el campo notes (útil para tokens largos)
- `bw list items --search <name>` — busca ítems por nombre
- La sesión expira al reiniciar. Re-unlock: `export BW_SESSION=$(bw unlock --raw)`
- Fallback: si `BW_SESSION` no está set, carga desde `~/.env` o `.env` local

## .env fallback structure

```bash
ANTHROPIC_API_KEY=""
GEMINI_API_KEY=""
GITHUB_PERSONAL_ACCESS_TOKEN=""
LINEAR_API_KEY=""
# ... resto de keys vacías, se rellenan desde bw en runtime
```

## Caveats

- `snap install bw` instala una versión con sandbox que puede fallar con `--raw`. Usar `npm install -g @bitwarden/cli` si falla.
- Nunca hacer `echo $BW_SESSION` en logs — es el token de sesión completo.

## Related

[[wiki/patterns]] | [[wiki/sources]]
