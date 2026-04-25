# Personal OS - CLAUDE.md

Este archivo es el contrato operativo para Claude Code dentro del vault
Obsidian-compatible de JarvisOS. Prioriza memoria local, trazabilidad y cambios
pequenos, verificables y reversibles.

## Identidad

- Motor principal: Claude Code.
- Sistema: JarvisOS Personal OS v2.
- Base de conocimiento: vault Markdown local, compatible con Obsidian.
- Modo por defecto: local-first, pragmatico, con evidencia antes de conclusion.
- Usuario principal: Marcos Arango.

## Arquitectura

JarvisOS se organiza como un sistema operativo personal con capas claras:

- Dashboard / interfaz unificada para operar busqueda, jobs, ingesta y seguridad.
- Kernel agentic en `jarvis_os/kernel/service.py`.
- Modulos funcionales: Daily OS, Projects, Research, Dev y Skills.
- Integraciones locales: MarkItDown, scanner regex, repositorios JSON y MCP.
- Vault Obsidian como sistema nervioso de memoria persistente.
- Runtime JSON bajo `data/runtime/` para jobs, eventos, ingestas y findings.

## Estructura del vault

- `00-Daily/`: logs, tareas, inbox operativo, agenda y revisiones.
- `01-Projects/`: specs, ADRs, roadmaps, entregas y planes por proyecto.
- `02-Research/`: fuentes, sintesis, MOCs, areas de aprendizaje y analisis.
- `03-Dev/`: snippets, patrones, documentacion tecnica y referencias.
- `04-Skills/`: skills, prompts, templates y configuraciones.
- `05-Inbox/`: documentos sin procesar para conversion o clasificacion.
- `assets/`: imagenes, diagramas y adjuntos.

## Stack de desarrollo

- Python + FastAPI para API, dashboard y kernel.
- Pydantic para contratos de datos en `jarvis_os/schemas.py`.
- Repositorios JSON append/replace para persistencia local ligera.
- Jinja templates para dashboard.
- Pytest para regresiones del kernel e integraciones.
- Markdown + YAML frontmatter como formato canonico de conocimiento.

## Pipeline RAG

El pipeline RAG actual es incremental y local-first:

1. Captura de documentos en `05-Inbox/` o rutas explicitas.
2. Conversion a Markdown mediante MarkItDown cuando esta disponible.
3. Fallback textual para formatos legibles como `.md`, `.txt`, `.csv`, `.json`,
   `.xml` y `.html`.
4. Escritura de notas normalizadas en `02-Research/`.
5. Chunking basico por encabezados `##` para medir unidades recuperables.
6. Retrieval textual sobre el vault.
7. Sintesis posterior por Claude Code cuando el usuario lo solicita.

Todavia no hay vector DB dedicada. Cualquier modo semantico debe declararse como
fallback textual y marcar `supported=False` hasta que existan embeddings reales.

## MarkItDown

`markitdown_convert` debe producir efectos observables:

- Crear una nota Markdown normalizada en `vault/02-Research/`.
- Registrar la conversion en `data/runtime/ingestions.json`.
- Devolver un job `succeeded` solo si la conversion termino en estado
  `converted`.

No basta con registrar el job. La conversion debe llamar a
`MarkItDownIngestor.convert(...)` y persistir el resultado.

## Búsqueda en vault

Modos soportados:

- `text`: busqueda textual real sobre notas del vault.
- `semantic`: degradacion explicita a busqueda textual hasta que haya backend
  vectorial.
- `ask_claude`: recupera contexto textual para que Claude sintetice despues.

Cuando se use `semantic` o `ask_claude`, la respuesta debe incluir un aviso claro
de degradacion y `supported=False`. No prometas embeddings, ranking vectorial ni
memoria semantica si no estan implementados.

## Ingesta

Reglas para nuevas notas generadas:

- Mantener frontmatter YAML con `title`, `type`, `status`, `tags`, `created`,
  `updated`, `tokens_consumed`, `sources` y `Summary` cuando aplique.
- Preservar la fuente original siempre que sea posible.
- Separar material de aprendizaje BJJ de implementacion del proyecto bjj-app.
- Preferir nombres de archivo lowercase, descriptivos y con guiones.

## Regex de seguridad

`security_scan` usa un scanner regex local para detectar secretos comunes antes
de commit o publicacion. Debe:

- Escanear artefactos o repositorios segun `SecurityScanRequest`.
- Persistir findings en `data/runtime/security-findings.json`.
- Reportar patron, severidad, path, linea, match y contexto.
- Mantenerse conservador: detectar sin modificar archivos.

Patrones esperados incluyen claves AWS, JWT y otros secretos definidos en
`jarvis_os/integrations/security.py`.

## Jobs

`KernelService.create_job()` debe ejecutar el job de forma real mediante
`_run_job()` y no limitarse a encolarlo. Cada job debe dejar trazabilidad en:

- `data/runtime/jobs.json`.
- `data/runtime/events.json`.
- Repositorios especificos cuando aplique: ingestas o findings.

## MCP e integraciones

Los MCP servers son adaptadores de capacidad, no sustitutos de memoria local.
Usalos cuando el vault no tenga suficiente contexto o cuando el usuario pida una
fuente externa concreta. Las credenciales deben vivir fuera del repositorio o en
archivos ignorados.

## Roadmap

- Vector DB local para busqueda semantica real.
- Reranking y scoring explicito de resultados.
- Clasificacion automatica de inbox por modulo.
- Pre-commit hook de seguridad instalado por job.
- Evaluaciones de calidad para ingesta y retrieval.
- Sincronizacion mas rica con Obsidian y MCP.

## Instrucciones para Claude Code

- Lee primero el contexto local relevante antes de editar.
- Mantén los cambios acotados al objetivo.
- No reviertas cambios sucios no relacionados.
- Si una capacidad aun es fallback, dilo explicitamente.
- Anade tests cuando cierres huecos de comportamiento del kernel.
- Ejecuta pytest o el subconjunto relevante antes de entregar.
- Actualiza este archivo desde `VaultMigrator._default_claude_md()` cuando cambie
  el contrato operativo del vault.
