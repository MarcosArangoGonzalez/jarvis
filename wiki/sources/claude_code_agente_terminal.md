---
title: "Claude Code: agente de terminal de Anthropic"
type: source
status: draft
tags:
  - article
  - claude
  - ai-tools
  - developer-tools
  - anthropic
created: 2026-04-16
updated: 2026-04-16
tokens_consumed: 350
sources:
  - "texto manual"
Summary: "Claude Code es el agente de terminal de Anthropic que permite trabajar con bases de código completas desde la línea de comandos, ejecutar comandos, leer y escribir ficheros, y colaborar en proyectos complejos."
requires_verification: false
---

# Claude Code: agente de terminal de Anthropic

## Resumen

Claude Code es el agente de terminal de Anthropic para desarrollo de software.
Permite trabajar con bases de código completas desde la línea de comandos,
ejecutar comandos, leer y escribir ficheros, y colaborar en proyectos complejos.
Es una herramienta local-first que integra las capacidades del modelo Claude
directamente en el flujo de trabajo del desarrollador.

## Conceptos clave

- **Agente de terminal**: interfaz CLI que ejecuta Claude con acceso al sistema de ficheros local y a herramientas de shell.
- **Bases de código completas**: capacidad de leer, indexar y modificar proyectos enteros, no sólo ficheros sueltos.
- **Ejecución de comandos**: puede invocar comandos de terminal dentro de la conversación (con permiso del usuario).
- **Colaboración en proyectos complejos**: mantiene contexto a lo largo de sesiones largas, usa `CLAUDE.md` como memoria persistente del proyecto.

## Casos de uso

1. Refactorizar código guiado por lenguaje natural.
2. Depurar errores buscando en todo el repositorio.
3. Generar documentación técnica a partir del código.
4. Automatizar flujos de trabajo con skills y hooks.
5. Integrar con MCP servers para acceso a herramientas externas (GitHub, Linear, etc.).

## Verificación pendiente

- [ ] Confirmar versión actual y modelo que utiliza por defecto
- [ ] Verificar compatibilidad con WSL / entornos remotos

## Related

[[jarvis_overview]] | [[tools_mcp_servers]]
