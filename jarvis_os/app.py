from __future__ import annotations

from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .api.routers import architecture, inbox, integrations, jobs, metrics, modules, overview, security, sessions, skills, vault
from .config import get_settings
from .kernel.service import KernelService
from .schemas import VaultSearchQuery


def create_app(*, enable_scheduler: bool = True) -> FastAPI:
    settings = get_settings()
    templates = Jinja2Templates(directory=str(settings.templates_dir))

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        scheduler = None
        if enable_scheduler:
            scheduler = BackgroundScheduler(daemon=True)
            scheduler.add_job(lambda: app.state.kernel.create_job(kind="health_snapshot"), "interval", minutes=30)
            scheduler.start()
        app.state.scheduler = scheduler
        yield
        if scheduler is not None:
            scheduler.shutdown(wait=False)

    app = FastAPI(title="JarvisOS Personal OS", lifespan=lifespan)
    app.state.settings = settings
    app.state.kernel = KernelService(settings)
    app.mount("/static", StaticFiles(directory=str(settings.static_dir)), name="static")

    for router in (
        overview.router,
        architecture.router,
        sessions.router,
        skills.router,
        jobs.router,
        inbox.router,
        security.router,
        vault.router,
        integrations.router,
        metrics.router,
        modules.router,
    ):
        app.include_router(router)

    @app.get("/", response_class=HTMLResponse)
    def dashboard(request: Request):
        context = {"request": request, "overview": app.state.kernel.get_overview()}
        return templates.TemplateResponse("overview.html", context)

    @app.get("/architecture", response_class=HTMLResponse)
    def dashboard_architecture(request: Request):
        context = {"request": request, "topology": app.state.kernel.get_topology()}
        return templates.TemplateResponse("architecture.html", context)

    @app.get("/sessions", response_class=HTMLResponse)
    def dashboard_sessions(request: Request):
        context = {"request": request, "sessions": app.state.kernel.get_sessions()}
        return templates.TemplateResponse("sessions.html", context)

    @app.get("/skills", response_class=HTMLResponse)
    def dashboard_skills(request: Request):
        context = {"request": request, "skills": app.state.kernel.get_skills()}
        return templates.TemplateResponse("skills.html", context)

    @app.get("/jobs", response_class=HTMLResponse)
    def dashboard_jobs(request: Request):
        context = {"request": request, "jobs": app.state.kernel.get_jobs()}
        return templates.TemplateResponse("jobs.html", context)

    @app.get("/inbox", response_class=HTMLResponse)
    def dashboard_inbox(request: Request):
        context = {"request": request, "items": app.state.kernel.get_inbox(), "ingestions": app.state.kernel.get_ingestions()}
        return templates.TemplateResponse("inbox.html", context)

    @app.get("/security", response_class=HTMLResponse)
    def dashboard_security(request: Request):
        context = {"request": request, "findings": app.state.kernel.get_security_findings()}
        return templates.TemplateResponse("security.html", context)

    @app.post("/jobs/run")
    def run_job(request: Request, kind: str = Form(...)):
        app.state.kernel.create_job(kind=kind)
        return RedirectResponse(url="/jobs", status_code=303)

    @app.post("/inbox/process")
    def process_inbox(path: str = Form(""), all_items: str = Form("")):
        if all_items:
            app.state.kernel.create_job(kind="inbox_process")
        elif path:
            app.state.kernel.create_job(kind="markitdown_convert", payload={"path": path})
        return RedirectResponse(url="/inbox", status_code=303)

    @app.post("/security/scan")
    def run_security_scan(path: str = Form("."), mode: str = Form("repo")):
        app.state.kernel.create_job(kind="security_scan", payload={"path": path, "mode": mode})
        return RedirectResponse(url="/security", status_code=303)

    @app.get("/vault/search", response_class=HTMLResponse)
    def dashboard_vault_search(
        request: Request,
        query: str = "",
        mode: str = "text",
        folder: str = "all",
        date_filter: str = "any",
    ):
        payload = VaultSearchQuery(
            query=query,
            mode=mode,  # type: ignore[arg-type]
            folder=folder,
            date_filter=date_filter,  # type: ignore[arg-type]
        )
        context = {
            "request": request,
            "result": app.state.kernel.search_vault(payload),
            "counts": app.state.kernel.workspace.vault_counts(),
            "query": payload,
        }
        return templates.TemplateResponse("vault_search.html", context)

    @app.get("/modules/{module_name}", response_class=HTMLResponse)
    def dashboard_module(module_name: str, request: Request):
        context = {"request": request, "module": app.state.kernel.get_module_state(module_name)}
        return templates.TemplateResponse("module.html", context)

    @app.get("/integrations", response_class=HTMLResponse)
    def dashboard_integrations(request: Request):
        context = {"request": request, "integrations": app.state.kernel.get_integrations()}
        return templates.TemplateResponse("integrations.html", context)

    return app


app = create_app()
