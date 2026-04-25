from __future__ import annotations

import subprocess
import sys
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from ..config import Settings
from ..integrations.legacy import LegacyWorkspace
from ..integrations.markitdown import MarkItDownIngestor
from ..integrations.security import SecurityRegexScanner
from ..integrations.vault import VaultMigrator
from ..repositories import EventRepository, IngestionRepository, JobRepository, SecurityFindingRepository
from ..schemas import (
    DashboardMetric,
    DashboardOverview,
    DashboardTask,
    Event,
    Job,
    MCPServerStatus,
    ModuleState,
    QuickAction,
    SecurityScanRequest,
    Session,
    SkillRunnerResult,
    TopologyLayer,
    TopologyMap,
    TopologyNode,
    VaultNoteSummary,
    VaultSearchQuery,
    VaultSearchResult,
)


class KernelService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.workspace = LegacyWorkspace(settings)
        self.migrator = VaultMigrator(settings)
        self.ingestor = MarkItDownIngestor(settings)
        self.security = SecurityRegexScanner(settings)
        self.jobs = JobRepository(settings.runtime_dir / "jobs.json")
        self.events = EventRepository(settings.runtime_dir / "events.json")
        self.ingestions = IngestionRepository(settings.runtime_dir / "ingestions.json")
        self.security_findings = SecurityFindingRepository(settings.runtime_dir / "security-findings.json")
        self.settings.runtime_dir.mkdir(parents=True, exist_ok=True)

    def get_overview(self) -> DashboardOverview:
        tasks = [
            DashboardTask(
                title=row["title"],
                project=row["project"],
                status=row["status"],
                priority=row["priority"],
            )
            for row in self.workspace.task_table(limit=5)
        ]
        sessions = self.workspace.recent_sessions(limit=4)
        recent_notes = self.workspace.recent_notes(limit=6)
        counts = self.workspace.vault_counts()
        return DashboardOverview(
            today=tasks,
            agenda=[
                "Morning coffee y revisión de prioridades.",
                "Procesar jobs manuales desde el dashboard.",
                "Buscar contexto en el vault antes de ejecutar cambios.",
            ],
            recent_notes=recent_notes,
            sessions=sessions,
            metrics=[
                DashboardMetric(label="Notas en vault", value=str(counts["all"]), hint="wiki/*.md indexado"),
                DashboardMetric(label="Skills", value=str(len(self.workspace.list_skills())), hint="tools/skills activos"),
                DashboardMetric(label="MCP", value=str(len(self.workspace.list_integrations())), hint="servers configurados"),
                DashboardMetric(label="Jobs guardados", value=str(len(self.jobs.load())), hint="runtime local"),
                DashboardMetric(label="Inbox", value=str(len(self.ingestor.list_inbox())), hint="vault/05-Inbox"),
            ],
            quick_actions=[
                QuickAction(label="Vault search", href="/vault/search"),
                QuickAction(label="Arquitectura", href="/architecture"),
                QuickAction(label="Sesiones", href="/sessions"),
                QuickAction(label="Skills", href="/skills"),
            ],
        )

    def get_skills(self):
        return self.workspace.list_skills()

    def get_sessions(self) -> list[Session]:
        return self.workspace.recent_sessions(limit=12)

    def get_session(self, session_id: str) -> Session | None:
        for session in self.get_sessions():
            if session.id == session_id:
                return session
        return None

    def get_integrations(self) -> list[MCPServerStatus]:
        return self.workspace.list_integrations()

    def get_inbox(self):
        return self.ingestor.list_inbox()

    def get_ingestions(self):
        return self.ingestions.load()

    def scan_security(self, request: SecurityScanRequest):
        return self.security.scan(request)

    def get_security_findings(self):
        return self.security_findings.load()

    def get_jobs(self) -> list[Job]:
        return self.jobs.load()

    def get_skill(self, skill_id: str):
        for skill in self.get_skills():
            if skill.id == skill_id:
                return skill
        return None

    def get_metrics(self) -> list[DashboardMetric]:
        jobs = self.jobs.load()
        events = self.events.load()
        success_count = len([job for job in jobs if job.status == "succeeded"])
        failed_count = len([job for job in jobs if job.status == "failed"])
        return [
            DashboardMetric(label="Jobs OK", value=str(success_count), hint="histórico runtime"),
            DashboardMetric(label="Jobs failed", value=str(failed_count), hint="requieren revisión"),
            DashboardMetric(label="Events", value=str(len(events)), hint="observabilidad estructurada"),
            DashboardMetric(label="Session log", value=str(len(self.get_sessions())), hint="sesiones recientes detectadas"),
        ]

    def get_module_state(self, name: str) -> ModuleState:
        mapping = {
            "dev": ("Dev", "Código, reviews y documentación técnica.", "dev"),
            "research": ("Research", "Notas, síntesis y material de RAG/agents.", "research"),
            "projects": ("Projects", "Project logs, roadmaps y tareas activas.", "projects"),
            "daily": ("Daily OS", "Tareas, sesiones y rutina operativa diaria.", "daily"),
        }
        title, description, category = mapping.get(name, ("Module", "Estado del módulo.", "research"))
        return ModuleState(
            name=name,
            title=title,
            description=description,
            badges=[f"{len(self.workspace.recent_notes(category=category, limit=20))} notas", "local-first"],
            items=self.workspace.recent_notes(category=category, limit=8),
            quick_actions=[
                QuickAction(label="Abrir vault search", href=f"/vault/search?folder={category}"),
                QuickAction(label="Ver sesiones", href="/sessions"),
            ],
        )

    def get_topology(self) -> TopologyMap:
        counts = self.workspace.vault_counts()
        return TopologyMap(
            title="Personal OS — Arquitectura del Sistema",
            layers=[
                TopologyLayer(
                    id="dashboard",
                    title="Interfaz unificada / Dashboard",
                    description="Panel modular y operativo del Personal OS.",
                    nodes=[
                        TopologyNode(
                            id="dashboard-root",
                            title="Dashboard",
                            subtitle="overview · sesiones · vault search",
                            items=["Operaciones", "Knowledge map", "Quick actions"],
                            tone="neutral",
                        )
                    ],
                ),
                TopologyLayer(
                    id="engine",
                    title="Claude Code / Kernel agentic",
                    description="Capa de control, orquestación y memoria operativa.",
                    nodes=[
                        TopologyNode(id="dev", title="Dev", subtitle="código · PR · tests", tone="violet"),
                        TopologyNode(id="research", title="Research", subtitle="RAG · síntesis", tone="violet"),
                        TopologyNode(id="projects", title="Projects", subtitle="roadmap · tareas", tone="violet"),
                        TopologyNode(id="daily", title="Daily OS", subtitle="journal · agenda", tone="violet"),
                    ],
                ),
                TopologyLayer(
                    id="mcp",
                    title="MCP Servers — capa de herramientas",
                    description="Integraciones y conectores externos visibles desde el kernel.",
                    nodes=[
                        TopologyNode(
                            id="mcp-servers",
                            title="Integraciones",
                            subtitle="obsidian · markitdown · linear · notion · drive · github",
                            items=[server.name for server in self.get_integrations()],
                            tone="blue",
                        )
                    ],
                ),
                TopologyLayer(
                    id="rag",
                    title="Pipeline RAG — ingesta y retrieval",
                    description="MarkItDown, chunking semantico, retrieval y escritura en vault.",
                    nodes=[
                        TopologyNode(id="inbox", title="05-Inbox", subtitle=f"{len(self.ingestor.list_inbox())} pendientes", tone="blue"),
                        TopologyNode(id="markitdown", title="MarkItDown", subtitle="Python first", tone="blue"),
                        TopologyNode(id="chunks", title="Chunks", subtitle="headers Markdown", tone="blue"),
                        TopologyNode(id="retrieval", title="Retrieval", subtitle="texto · semantico · Claude", tone="blue"),
                    ],
                ),
                TopologyLayer(
                    id="vault",
                    title="Capa de datos — vault como sistema nervioso",
                    description="Memoria duradera basada en Markdown y taxonomía operativa.",
                    nodes=[
                        TopologyNode(id="knowledge", title="Knowledge", subtitle=f"{counts['research']} notas", tone="amber"),
                        TopologyNode(id="projects-data", title="Projects", subtitle=f"{counts['projects']} notas", tone="amber"),
                        TopologyNode(id="daily-data", title="Daily OS", subtitle=f"{counts['daily']} notas", tone="amber"),
                        TopologyNode(id="dev-data", title="Codebase", subtitle=f"{counts['dev']} notas", tone="amber"),
                        TopologyNode(id="skills-data", title="Skills", subtitle=f"{counts['skills']} notas", tone="amber"),
                    ],
                ),
                TopologyLayer(
                    id="output",
                    title="Output",
                    description="Artefactos y decisiones producidas por JarvisOS.",
                    nodes=[
                        TopologyNode(
                            id="outputs",
                            title="Outputs",
                            items=["código", "documentación", "decisiones", "investigación", "tareas"],
                            tone="red",
                        )
                    ],
                ),
            ],
        )

    def search_vault(self, query: VaultSearchQuery) -> VaultSearchResult:
        notice = ""
        supported = True
        if query.mode == "semantic":
            notice = "Modo semántico aún no tiene backend vectorial dedicado; se usa fallback textual."
            supported = False
        if query.mode == "ask_claude":
            notice = "Modo preguntar a Claude devuelve contexto del vault para síntesis posterior; fallback textual activo."
            supported = False
        items = self.workspace.search_notes(
            query=query.query,
            folder=query.folder,
            tags=query.tags,
            date_filter=query.date_filter,
        )
        return VaultSearchResult(
            total=len(items),
            mode=query.mode,
            supported=supported,
            notice=notice,
            items=items,
        )

    def create_job(self, *, kind: str, payload: dict | None = None) -> Job:
        payload = payload or {}
        now = datetime.now()
        job = Job(
            id=f"job-{uuid4().hex[:10]}",
            kind=kind,
            title=kind.replace("_", " ").title(),
            status="queued",
            created_at=now,
            payload=payload,
        )
        self.jobs.add(job)
        self._emit_event("job.started", job.id, f"Job {job.kind} started", "job", {"payload": payload})
        return self._run_job(job)

    def _run_job(self, job: Job) -> Job:
        job.status = "running"
        job.started_at = datetime.now()
        self.jobs.update(job)
        if job.kind == "health_snapshot":
            result = SkillRunnerResult(
                status="succeeded",
                started_at=job.started_at,
                finished_at=datetime.now(),
                duration_ms=1,
                stdout_excerpt="Health snapshot stored in runtime repositories.",
                data={
                    "sessions": len(self.get_sessions()),
                    "skills": len(self.get_skills()),
                    "integrations": len(self.get_integrations()),
                },
            )
            job.result = result
            job.status = "succeeded"
        elif job.kind == "vault_migrate":
            stats = self.migrator.migrate(limit=job.payload.get("limit"))
            job.result = SkillRunnerResult(
                status="succeeded",
                started_at=job.started_at,
                finished_at=datetime.now(),
                duration_ms=1,
                stdout_excerpt=f"Vault migration copied {stats['copied']} files, skipped {stats['skipped']}.",
                data=stats,
            )
            job.status = "succeeded"
        elif job.kind == "markitdown_convert":
            source = job.payload.get("path", "")
            conversion = self.ingestor.convert(Path(source))
            self.ingestions.add(conversion)
            job.result = SkillRunnerResult(
                status="succeeded" if conversion.status == "converted" else "failed",
                started_at=job.started_at,
                finished_at=datetime.now(),
                duration_ms=1,
                artifacts=[{"label": "Converted note", "path": conversion.output_path}] if conversion.output_path else [],
                stdout_excerpt=conversion.output_path or conversion.error,
                error_excerpt=conversion.error,
                data=conversion.model_dump(mode="json"),
            )
            job.status = "succeeded" if conversion.status == "converted" else "failed"
        elif job.kind == "inbox_process":
            results = []
            for item in self.ingestor.list_inbox():
                conversion = self.ingestor.convert(Path(item.path))
                self.ingestions.add(conversion)
                results.append(conversion)
            failures = [item for item in results if item.status == "failed"]
            job.result = SkillRunnerResult(
                status="failed" if failures else "succeeded",
                started_at=job.started_at,
                finished_at=datetime.now(),
                duration_ms=1,
                stdout_excerpt=f"Processed {len(results)} inbox items with {len(failures)} failures.",
                data={"items": [item.model_dump(mode="json") for item in results]},
            )
            job.status = "failed" if failures else "succeeded"
        elif job.kind == "security_scan":
            scan = self.security.scan(SecurityScanRequest(**job.payload))
            self.security_findings.replace(scan.findings)
            job.result = SkillRunnerResult(
                status="succeeded",
                started_at=job.started_at,
                finished_at=datetime.now(),
                duration_ms=1,
                stdout_excerpt=f"{len(scan.findings)} findings across {scan.files_scanned} files.",
                data=scan.model_dump(mode="json"),
            )
            job.status = "succeeded"
        elif job.kind == "precommit_hook_generate":
            output = self.settings.runtime_dir / "pre-commit-security-scan.sh"
            output.write_text(self.security.precommit_hook(), encoding="utf-8")
            job.result = SkillRunnerResult(
                status="succeeded",
                started_at=job.started_at,
                finished_at=datetime.now(),
                duration_ms=1,
                artifacts=[{"label": "Pre-commit hook", "path": str(output.relative_to(self.settings.root_dir))}],
                stdout_excerpt=str(output.relative_to(self.settings.root_dir)),
            )
            job.status = "succeeded"
        elif job.kind == "whatsapp_backlog_dry_run":
            result = self._run_subprocess_job(
                [sys.executable, str(self.settings.root_dir / "tools" / "skills" / "process_whatsapp_backlog.py"), "--dry-run"]
            )
            job.result = result
            job.status = "succeeded" if result.error_excerpt == "" else "failed"
        else:
            job.status = "failed"
            job.error = f"Unsupported job kind: {job.kind}"
            job.result = SkillRunnerResult(
                status="failed",
                started_at=job.started_at,
                finished_at=datetime.now(),
                duration_ms=0,
                error_excerpt=job.error,
            )
        job.finished_at = datetime.now()
        self.jobs.update(job)
        level = "info" if job.status == "succeeded" else "error"
        self._emit_event(f"job.{job.status}", job.id, f"Job {job.kind} {job.status}", "job", {"status": job.status}, level=level)
        return job

    def _run_subprocess_job(self, command: list[str]) -> SkillRunnerResult:
        started_at = datetime.now()
        try:
            completed = subprocess.run(
                command,
                cwd=self.settings.root_dir,
                capture_output=True,
                text=True,
                timeout=120,
            )
        except Exception as exc:
            return SkillRunnerResult(
                status="failed",
                started_at=started_at,
                finished_at=datetime.now(),
                duration_ms=int((datetime.now() - started_at).total_seconds() * 1000),
                error_excerpt=str(exc),
            )
        return SkillRunnerResult(
            status="succeeded" if completed.returncode == 0 else "failed",
            started_at=started_at,
            finished_at=datetime.now(),
            duration_ms=int((datetime.now() - started_at).total_seconds() * 1000),
            stdout_excerpt=completed.stdout[:500],
            error_excerpt=completed.stderr[:500],
        )

    def _emit_event(
        self,
        kind: str,
        entity_id: str,
        message: str,
        entity_type: str,
        data: dict,
        *,
        level: str = "info",
    ) -> Event:
        event = Event(
            id=f"evt-{uuid4().hex[:10]}",
            kind=kind,
            level=level,  # type: ignore[arg-type]
            timestamp=datetime.now(),
            entity_type=entity_type,
            entity_id=entity_id,
            message=message,
            data=data,
        )
        return self.events.add(event)
