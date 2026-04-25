---
name: bridge
description: Conecta sesiones de planificación en claude.ai con Claude Code en terminal. Preserva contexto entre el chat y el terminal exportando planes al vault y generando SESSION.md. Úsala ante frases como guardar este plan, exportar al vault, prepara contexto para terminal, sincroniza sesión o no perder contexto.
---

# bridge skill — claude.ai ↔ Claude Code

## El problema que resuelve

Claude.ai (planning, diagramas, brainstorming) y Claude Code (terminal, implementación)
son dos contextos separados. Sin este puente, el contexto se pierde entre sesiones.

## 5 pasos — hacer ahora mismo

### Paso 1 — vault como puente (5 min, una vez)

Al terminar una sesión de planificación aquí:
```bash
/jarvis-log
```
Al terminar una sesión en Claude Code:
```bash
/jarvis-log
```
El vault es el estado compartido. Cualquier agente que lea vault/CLAUDE.md
tiene el contexto de lo que pasó.

### Paso 2 — exportar plan de este chat al vault (2 min)

Pedir en claude.ai: "Guarda este plan como nota de vault"
Claude genera el .md con frontmatter correcto listo para:
- vault/01-Projects/ — plan de proyecto
- vault/02-Research/ — investigación
- vault/00-Daily/ — journal del día

Copiar el fichero generado. Fin.

### Paso 3 — SESSION.md como contexto inicial (inmediato)

```bash
touch /home/marcos/jarvis/SESSION.md
```

Flujo:
1. En claude.ai pide "genera el SESSION.md para esta sesión"
2. Claude genera el fichero con el contexto del plan actual
3. Copiar contenido a SESSION.md antes de abrir Claude Code
4. Claude Code lo lee automáticamente al arrancar
5. Tiempo total: 10 segundos

Contenido típico de SESSION.md:
```markdown
# Sesión activa — YYYY-MM-DD

## Contexto del plan
[resumen del plan de claude.ai]

## Tarea actual
[qué se va a implementar]

## Decisiones tomadas
[decisiones de arquitectura del chat]

## Referencias
- vault/01-Projects/[plan].md
- vault/CLAUDE.md
```

### Paso 4 — ccusage (2 min, una vez)

```bash
npm install -g ccusage
ccusage
```

Dashboard de consumo de tokens por sesión.
Sin esto no tienes visibilidad del gasto real.

### Paso 5 — Context7 (30 segundos, una vez)

```bash
claude mcp add context7 -- npx -y @upstash/context7-mcp@latest
```

Desde ese momento en cualquier prompt de Claude Code:
```
"Implementa autenticación JWT. use context7"
```
Fetcha docs actuales de la librería antes de generar código.

## Comandos de uso frecuente

```bash
# Al empezar el día
/jarvis-log        # ver estado del vault
/morning_coffee    # briefing con contexto del día

# Al terminar sesión de planning (claude.ai → Claude Code)
# 1. Pedir "genera SESSION.md" en claude.ai
# 2. Copiar a /home/marcos/jarvis/SESSION.md
# 3. Abrir Claude Code — contexto cargado

# Al terminar sesión de implementación (Claude Code → vault)
/jarvis-log        # guarda resumen en vault
/jarvis-commit     # commit con cambios del vault
```

## Lo que NO hacer ahora

No malgastar tiempo en WebSocket embebido, Electron, auth profesional
ni configuraciones complejas de MCP. Eso es Fase 1 del plan — para después.
El vault como puente es la solución 80/20: funciona hoy, escala cuando
el dashboard esté implementado.
