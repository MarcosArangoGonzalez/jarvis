from __future__ import annotations

import shutil
import re
from pathlib import Path

from ..config import Settings
from ..schemas import VaultGraph, VaultGraphEdge, VaultGraphNode


class VaultMigrator:
    """Non-destructive wiki -> vault copier for the Personal OS v2 layout."""

    FOLDERS = ("00-Daily", "01-Projects", "02-Research", "03-Dev", "04-Skills", "05-Inbox", "assets")
    WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)")

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def ensure_layout(self) -> list[Path]:
        created: list[Path] = []
        self.settings.vault_dir.mkdir(parents=True, exist_ok=True)
        for folder in self.FOLDERS:
            path = self.settings.vault_dir / folder
            if not path.exists():
                path.mkdir(parents=True)
                created.append(path)
        return created

    def migrate(self, *, limit: int | None = None) -> dict[str, int]:
        self.ensure_layout()
        copied = 0
        skipped = 0
        for source in sorted(self.settings.wiki_dir.rglob("*.md")):
            target = self._target_for(source)
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                skipped += 1
                continue
            shutil.copy2(source, target)
            copied += 1
            if limit is not None and copied >= limit:
                break
        claude_md = self.settings.vault_dir / "CLAUDE.md"
        if not claude_md.exists():
            claude_md.write_text(self._default_claude_md(), encoding="utf-8")
            copied += 1
        return {"copied": copied, "skipped": skipped}

    def _target_for(self, source: Path) -> Path:
        rel = source.relative_to(self.settings.wiki_dir)
        raw = str(rel).lower()
        if raw.startswith("tasks/") or raw.startswith("logs/"):
            base = "00-Daily"
        elif raw.startswith("projects/"):
            base = "01-Projects"
        elif raw.startswith("sources/") or raw.startswith("analyses/") or raw.startswith("areas/"):
            base = "02-Research"
        elif raw.startswith("patterns/") or raw.startswith("concepts/"):
            base = "03-Dev"
        else:
            base = "04-Skills"
        return self.settings.vault_dir / base / rel

    def build_graph(self, *, folder: str = "all", min_links: int = 0, tag: str = "") -> VaultGraph:
        notes = self._index_notes()
        title_map = {note.title.strip().lower(): note for note in notes}
        stem_map = {Path(note.id).stem.strip().lower(): note for note in notes}
        nodes_by_id: dict[str, VaultGraphNode] = {}
        edges: list[VaultGraphEdge] = []

        for note in notes:
            path = self.settings.root_dir / note.id
            text = path.read_text(encoding="utf-8", errors="replace")
            links = self.WIKILINK_RE.findall(text)
            resolved_targets: list[VaultGraphNode] = []
            for raw_link in links:
                key = raw_link.strip().lower()
                target = title_map.get(key) or stem_map.get(key)
                if target and target.id != note.id:
                    resolved_targets.append(target)
                    edges.append(VaultGraphEdge(source=note.id, target=target.id))

            node = note.model_copy(update={"links_count": len(resolved_targets)})
            if folder != "all" and node.folder != folder:
                continue
            if tag and tag not in node.tags:
                continue
            if node.links_count < min_links:
                continue
            nodes_by_id[node.id] = node

        visible_ids = set(nodes_by_id)
        visible_edges = [edge for edge in edges if edge.source in visible_ids and edge.target in visible_ids]
        return VaultGraph(nodes=list(nodes_by_id.values()), edges=visible_edges)

    def _index_notes(self) -> list[VaultGraphNode]:
        root = self.settings.vault_dir if self.settings.vault_dir.exists() else self.settings.wiki_dir
        notes: list[VaultGraphNode] = []
        for path in sorted(root.rglob("*.md")):
            if path.name.startswith(".") or path.name == "CLAUDE.md":
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            notes.append(
                VaultGraphNode(
                    id=str(path.relative_to(self.settings.root_dir)),
                    title=self._title_from_text(text, path),
                    folder=self._folder_for_path(path),
                    tags=re.findall(r'^\s*-\s+"?([a-zA-Z0-9:_#-]+)"?\s*$', text, flags=re.MULTILINE)[:8],
                )
            )
        return notes

    @staticmethod
    def _title_from_text(text: str, path: Path) -> str:
        frontmatter = re.search(r'^title:\s*"?([^"\n]+)"?\s*$', text, flags=re.MULTILINE)
        if frontmatter:
            return frontmatter.group(1).strip()
        heading = re.search(r"^#\s+(.+)$", text, flags=re.MULTILINE)
        if heading:
            return heading.group(1).strip()
        return path.stem.replace("-", " ").title()

    @staticmethod
    def _folder_for_path(path: Path) -> str:
        raw = str(path).lower()
        if "/vault/00-daily/" in raw or "/wiki/tasks/" in raw or "/wiki/logs/" in raw:
            return "daily"
        if "/vault/01-projects/" in raw or "/wiki/projects/" in raw:
            return "projects"
        if "/vault/02-research/" in raw or "/wiki/analyses/" in raw or "/wiki/sources/" in raw or "/wiki/areas/" in raw:
            return "research"
        if "/vault/03-dev/" in raw or "/wiki/patterns/" in raw:
            return "dev"
        if "/vault/04-skills/" in raw:
            return "skills"
        return "skills" if "/wiki/entities/" in raw else "research"

    @staticmethod
    def _default_claude_md() -> str:
        return """# Personal OS - CLAUDE.md

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

## Terminal Claude Code (Fase 1)

El dashboard expone un terminal local en `/terminal` con API en
`/api/terminal/sessions` y WebSocket en `/ws/terminal/{session_id}`. La sesión se
ejecuta con `claude --model <model>` dentro de `settings.root_dir` cuando
`load_vault_context=True`.

Limitaciones v1:

- Sesiones PTY en memoria del proceso FastAPI, sin persistencia histórica.
- Uso local en `127.0.0.1`; no hay hardening multiusuario ni exposición pública.
- Métricas básicas parseadas del stream; si Claude cambia el formato, quedan a
  cero sin romper el terminal.
- No inyecta contexto automáticamente al PTY: Claude Code lee el repo/vault desde
  el directorio raíz.

## Research Engine (Fase 2)

El dashboard expone `/research` y la API `POST /api/research/query` con backends
`perplexity`, `notebooklm` y `ollama`. Los resultados se guardan en
`data/runtime/research.json`.

Reglas v1:

- `perplexity` solo hace web research real si existe `PERPLEXITY_API_KEY`.
- `ollama` intenta `http://127.0.0.1:11434/api/generate`; si no está disponible,
  devuelve contexto recuperado del vault.
- `notebooklm` queda como adaptador no configurado y degrada a contexto del vault.
- `save_to_vault=True` crea `vault/02-Research/research-{slug}.md` con
  frontmatter y citas cuando existan.
- Las degradaciones deben marcar `supported=False` y explicar `notice`.

## Graph View (Fase 3)

El dashboard expone `/graph` y la API `GET /api/vault/graph`. El grafo usa notas
Markdown como nodos y wikilinks `[[Nota]]` como edges.

Reglas v1:

- El parser resuelve enlaces por `title` de frontmatter, encabezado `#` o stem
  del archivo.
- Filtros soportados: `folder`, `tag` y `min_links`.
- La visualización D3.js vive en `jarvis_os/dashboard/static/graph.js`.
- No hay embeddings ni ranking semántico en esta fase; solo enlaces explícitos.

## Notepad + Calendario (Fase 4)

El dashboard expone `/notepad`, `GET /api/notes/daily/today`,
`GET|PUT /api/notes/{path}` y `GET /api/calendar/events`.

Reglas v1:

- La escritura de notas está restringida a `vault/` y solo permite Markdown.
- Las notas nuevas reciben frontmatter automático con `title`, `type`, `status`,
  `created`, `updated` y `tokens_consumed`.
- El journal diario vive en `vault/00-Daily/journal-YYYY-MM-DD.md`.
- El calendario detecta eventos por fechas `YYYY-MM-DD` en nombres de archivo.
- El editor del dashboard auto-guarda cada 30 segundos.

## Búsqueda semántica (Fase 5)

El job `vault_reindex` crea `data/runtime/vault-index.db` con chunks del vault y
embeddings locales. `search_vault(mode="semantic")` usa ese índice cuando existe.

Reglas v1:

- Si el índice no existe, `semantic` degrada a búsqueda textual con
  `supported=False`.
- El índice usa SQLite local y no se recalcula en cada query.
- Las dependencias declaradas son `sqlite-vec` y `sentence-transformers`; la
  implementación mantiene un embedding hash local como fallback operativo.
- Reindexar después de cambios grandes en el vault.

## Newsletter diario (Fase 6)

El dashboard expone `/newsletter`, `POST /api/newsletter/generate`,
`GET /newsletter/{date}` y `GET /newsletter/{date}/html`. El job
`newsletter_generate` crea artefactos en
`vault/00-Daily/newsletters/YYYY-MM-DD.{md,html,pdf}`.

Reglas v1:

- La fuente activa sin credenciales es el vault local.
- Gmail queda como skill en `tools/skills/gmail/` y requiere OAuth externo.
- PDF se genera solo si `weasyprint` está instalado.
- El HTML usa CSS editorial aislado en `jarvis_os/dashboard/static/newsletter.css`.
- La skill principal vive en `tools/skills/newsletter/SKILL.md`.

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
"""
