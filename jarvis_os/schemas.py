from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


HealthStatus = Literal["healthy", "degraded", "unknown"]
JobStatus = Literal["queued", "running", "succeeded", "failed"]
SessionStatus = Literal["active", "completed", "unknown"]
SearchMode = Literal["text", "semantic", "ask_claude"]
ResearchBackend = Literal["perplexity", "notebooklm", "ollama"]
IngestionStatus = Literal["pending", "converted", "failed"]
SecuritySeverity = Literal["info", "warning", "high"]
TerminalStatus = Literal["active", "closed"]


class Agent(BaseModel):
    id: str
    name: str
    role: str
    status: SessionStatus = "active"
    capabilities: list[str] = Field(default_factory=list)
    policy: str = "semi-autonomous"


class SkillDefinition(BaseModel):
    id: str
    name: str
    kind: str
    entrypoint: str
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    supports_tokens: bool = False
    health_status: HealthStatus = "unknown"
    last_run_at: datetime | None = None


class ArtifactRef(BaseModel):
    label: str
    path: str


class SkillRunnerResult(BaseModel):
    status: JobStatus | Literal["ok"] = "succeeded"
    started_at: datetime | None = None
    finished_at: datetime | None = None
    duration_ms: int = 0
    tokens_in: int = 0
    tokens_out: int = 0
    tokens_total: int = 0
    artifacts: list[ArtifactRef] = Field(default_factory=list)
    stdout_excerpt: str = ""
    error_excerpt: str = ""
    data: dict[str, Any] = Field(default_factory=dict)


class Session(BaseModel):
    id: str
    title: str
    started_at: datetime | None = None
    finished_at: datetime | None = None
    status: SessionStatus = "unknown"
    project: str = "JarvisOS"
    role: str = "Senior Architect"
    summary: str = ""
    source_path: str = ""
    artifacts: list[ArtifactRef] = Field(default_factory=list)


class SessionMetrics(BaseModel):
    tokens_in: int = 0
    tokens_out: int = 0
    context_pct: float = 0.0
    model: str = ""
    cost_usd: float = 0.0
    elapsed_s: float = 0.0


class TerminalSessionCreate(BaseModel):
    cwd: str = "."
    model: str = "claude-sonnet-4-6"
    load_vault_context: bool = True


class TerminalSessionInfo(BaseModel):
    session_id: str
    cwd: str
    started_at: datetime
    status: TerminalStatus = "active"
    metrics: SessionMetrics = Field(default_factory=SessionMetrics)


class Job(BaseModel):
    id: str
    kind: str
    title: str
    status: JobStatus = "queued"
    created_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    result: SkillRunnerResult | None = None
    error: str = ""


class Event(BaseModel):
    id: str
    kind: str
    level: Literal["info", "warning", "error"] = "info"
    timestamp: datetime
    entity_type: str
    entity_id: str
    message: str
    data: dict[str, Any] = Field(default_factory=dict)


class VaultNoteSummary(BaseModel):
    path: str
    title: str
    summary: str = ""
    tags: list[str] = Field(default_factory=list)
    folder: str
    updated_at: datetime


class VaultSearchQuery(BaseModel):
    query: str = ""
    mode: SearchMode = "text"
    folder: str = "all"
    tags: list[str] = Field(default_factory=list)
    date_filter: Literal["any", "week", "month"] = "any"
    note_type: str = "all"


class VaultSearchResult(BaseModel):
    total: int
    mode: SearchMode
    supported: bool = True
    notice: str = ""
    items: list[VaultNoteSummary] = Field(default_factory=list)


class VaultGraphNode(BaseModel):
    id: str
    title: str
    folder: str
    tags: list[str] = Field(default_factory=list)
    links_count: int = 0


class VaultGraphEdge(BaseModel):
    source: str
    target: str


class VaultGraph(BaseModel):
    nodes: list[VaultGraphNode] = Field(default_factory=list)
    edges: list[VaultGraphEdge] = Field(default_factory=list)


class NoteWriteRequest(BaseModel):
    content: str


class NoteDocument(BaseModel):
    path: str
    title: str
    content: str
    updated_at: datetime


class CalendarEvent(BaseModel):
    date: str
    title: str
    path: str


class NewsletterItem(BaseModel):
    title: str
    source: str
    content: str
    url: str | None = None
    type: Literal["email", "rss", "web", "vault"]
    published: str = ""
    citations: list[str] = Field(default_factory=list)


class NewsletterSection(BaseModel):
    id: str
    title: str
    items: list[NewsletterItem] = Field(default_factory=list)


class NewsletterResult(BaseModel):
    date: str
    sections: list[NewsletterSection] = Field(default_factory=list)
    md_path: str
    html_path: str
    pdf_path: str | None = None
    generated_at: datetime
    items_total: int = 0


class ResearchQuery(BaseModel):
    query: str
    backend: ResearchBackend = "perplexity"
    model: str = "sonar"
    save_to_vault: bool = False
    notebook_id: str | None = None


class ResearchResult(BaseModel):
    id: str
    query: str
    answer: str
    backend: ResearchBackend
    model: str = ""
    citations: list[str] = Field(default_factory=list)
    vault_path: str | None = None
    cost_usd: float = 0.0
    created_at: datetime
    supported: bool = True
    notice: str = ""


class InboxItem(BaseModel):
    path: str
    name: str
    suffix: str
    size_bytes: int
    status: IngestionStatus = "pending"
    updated_at: datetime


class IngestionResult(BaseModel):
    source_path: str
    output_path: str = ""
    status: IngestionStatus
    title: str = ""
    error: str = ""
    chunks: int = 0


class SecurityScanRequest(BaseModel):
    path: str = "."
    mode: Literal["artifact", "repo"] = "repo"
    include_binary: bool = False


class SecurityFinding(BaseModel):
    pattern_id: str
    label: str
    severity: SecuritySeverity
    path: str
    line: int
    match: str
    context: str = ""


class SecurityScanResult(BaseModel):
    scanned_path: str
    findings: list[SecurityFinding] = Field(default_factory=list)
    files_scanned: int = 0


class MCPServerStatus(BaseModel):
    id: str
    name: str
    description: str = ""
    configured: bool = True
    available: bool = False
    authenticated: bool = False
    last_error: str = ""


class DashboardMetric(BaseModel):
    label: str
    value: str
    hint: str = ""


class DashboardTask(BaseModel):
    title: str
    project: str = ""
    status: str = ""
    priority: str = ""


class QuickAction(BaseModel):
    label: str
    href: str


class ModuleState(BaseModel):
    name: str
    title: str
    description: str
    badges: list[str] = Field(default_factory=list)
    items: list[VaultNoteSummary] = Field(default_factory=list)
    quick_actions: list[QuickAction] = Field(default_factory=list)


class DashboardOverview(BaseModel):
    today: list[DashboardTask] = Field(default_factory=list)
    agenda: list[str] = Field(default_factory=list)
    recent_notes: list[VaultNoteSummary] = Field(default_factory=list)
    sessions: list[Session] = Field(default_factory=list)
    metrics: list[DashboardMetric] = Field(default_factory=list)
    quick_actions: list[QuickAction] = Field(default_factory=list)


class TopologyNode(BaseModel):
    id: str
    title: str
    subtitle: str = ""
    items: list[str] = Field(default_factory=list)
    tone: str = "neutral"


class TopologyLayer(BaseModel):
    id: str
    title: str
    description: str
    nodes: list[TopologyNode] = Field(default_factory=list)


class TopologyMap(BaseModel):
    title: str
    layers: list[TopologyLayer] = Field(default_factory=list)


# --- Session Wizard ---

class ContextFile(BaseModel):
    name: str
    category: str
    path: str
    description: str = ""


class SessionWizardRequest(BaseModel):
    contexts: list[str] = Field(default_factory=list)
    profile: str | None = None
    save_profile: bool = False
    profile_name: str = ""


class SessionWizardResult(BaseModel):
    claude_md: str
    sources: list[str]
    saved_path: str | None = None


# --- CI/CD ---

class CiCdRun(BaseModel):
    workflow: str
    status: str
    conclusion: str | None = None
    created_at: str
    url: str


class CiCdStatus(BaseModel):
    available: bool
    runs: list[CiCdRun] = Field(default_factory=list)
    sonar_gate: str | None = None
    notice: str = ""


# --- Session Insights ---

class SessionInsight(BaseModel):
    title: str
    date: str
    technologies: list[str] = Field(default_factory=list)
    patterns_used: list[str] = Field(default_factory=list)
    path: str
    summary: str | None = None


# --- Doc Checker ---

class DocStatus(BaseModel):
    library: str
    version: str = ""
    summary: str = ""
    source: str = ""
    available: bool = False


class DocCheckRequest(BaseModel):
    libraries: list[str]
    save_to_vault: bool = False


class DocCheckResult(BaseModel):
    docs: list[DocStatus] = Field(default_factory=list)
    vault_path: str | None = None


# --- Renderer ---

RenderMode = Literal["mermaid", "claude", "auto"]


class RenderRequest(BaseModel):
    spec: str
    mode: RenderMode = "auto"
    title: str = ""


class RenderResult(BaseModel):
    mode: RenderMode
    output: str
    format: Literal["mermaid", "svg", "html"] = "mermaid"


# --- Dev Hub ---

class DevHubOverview(BaseModel):
    recent_jobs: list[Job] = Field(default_factory=list)
    recent_findings: list[SecurityFinding] = Field(default_factory=list)
    recent_insights: list[SessionInsight] = Field(default_factory=list)
    cicd: CiCdStatus = Field(default_factory=lambda: CiCdStatus(available=False))
    metrics: list[DashboardMetric] = Field(default_factory=list)
