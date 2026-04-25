from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


HealthStatus = Literal["healthy", "degraded", "unknown"]
JobStatus = Literal["queued", "running", "succeeded", "failed"]
SessionStatus = Literal["active", "completed", "unknown"]
SearchMode = Literal["text", "semantic", "ask_claude"]
IngestionStatus = Literal["pending", "converted", "failed"]
SecuritySeverity = Literal["info", "warning", "high"]


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
