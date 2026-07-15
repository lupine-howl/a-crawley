"""Dashboard shell routes (Jinja2 + HTMX)."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from crawley.llm.factory import llm_status
from crawley.modules.contract import Module
from crawley.jobs import JobState
from crawley.modules.gmail import GmailModule, authorization_url, finish_oauth
from crawley.modules.investment import InvestmentModule
from crawley.modules.registry import nav_modules

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

router = APIRouter()


def _base_url(request: Request) -> str:
    # Prefer localhost-style host for OAuth redirect consistency on WSL.
    url = str(request.base_url).rstrip("/")
    parsed = urlparse(url)
    host = parsed.hostname or "127.0.0.1"
    if host in {"0.0.0.0", "localhost"}:
        host = "127.0.0.1"
    port = parsed.port
    netloc = f"{host}:{port}" if port else host
    return f"{parsed.scheme}://{netloc}"


def _base_context(request: Request, registry: dict[str, Module]) -> dict[str, Any]:
    return {
        "request": request,
        "nav": nav_modules(registry),
        "llm": llm_status(),
    }


def _module_response(
    request: Request,
    module: Module,
    *,
    status_code: int = 200,
) -> HTMLResponse:
    registry: dict[str, Module] = request.app.state.registry
    ctx = _base_context(request, registry)
    ctx.update(
        {
            "active_id": module.meta.id,
            "module": module,
            "panel": module.panel_context(),
        }
    )
    template = "partials/panel.html" if request.headers.get("hx-request") == "true" else "module.html"
    return templates.TemplateResponse(request, template, ctx, status_code=status_code)


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request) -> HTMLResponse:
    registry: dict[str, Module] = request.app.state.registry
    ctx = _base_context(request, registry)
    ctx["active_id"] = None
    return templates.TemplateResponse(request, "dashboard.html", ctx)


@router.get("/modules/{module_id}", response_class=HTMLResponse)
def module_panel(request: Request, module_id: str) -> HTMLResponse:
    registry: dict[str, Module] = request.app.state.registry
    module = registry.get(module_id)
    if module is None:
        ctx = _base_context(request, registry)
        ctx.update({"active_id": None, "error": f"Unknown module: {module_id}"})
        return templates.TemplateResponse(request, "dashboard.html", ctx, status_code=404)
    return _module_response(request, module)


@router.post("/modules/investment/run", response_class=HTMLResponse)
def investment_run(request: Request, query: str = Form("US stock market outlook")) -> HTMLResponse:
    registry: dict[str, Module] = request.app.state.registry
    module = registry["investment"]
    assert isinstance(module, InvestmentModule)
    result = module.run({"query": query})
    if result.error and module.job.status != "busy":
        module.job.status = "error"
        module.job.message = result.error
    return _module_response(request, module)


@router.get("/modules/investment/status", response_class=HTMLResponse)
def investment_status(request: Request) -> HTMLResponse:
    module = request.app.state.registry["investment"]
    return _module_response(request, module)


@router.post("/modules/gmail/run", response_class=HTMLResponse)
def gmail_run(request: Request) -> HTMLResponse:
    module = request.app.state.registry["gmail"]
    assert isinstance(module, GmailModule)
    result = module.run({})
    if result.error and module.job.status != "busy":
        module.job.status = "error"
        module.job.message = result.error
    return _module_response(request, module)


@router.get("/modules/gmail/status", response_class=HTMLResponse)
def gmail_status(request: Request) -> HTMLResponse:
    module = request.app.state.registry["gmail"]
    return _module_response(request, module)


@router.get("/modules/gmail/oauth/start")
def gmail_oauth_start(request: Request) -> RedirectResponse:
    module = request.app.state.registry["gmail"]
    assert isinstance(module, GmailModule)
    try:
        url, state = authorization_url(_base_url(request))
        module.oauth_state = state
        return RedirectResponse(url)
    except Exception as exc:  # noqa: BLE001
        module.job = JobState(status="error", message=str(exc))
        return RedirectResponse("/modules/gmail", status_code=303)


@router.get("/modules/gmail/oauth/callback")
def gmail_oauth_callback(request: Request) -> RedirectResponse:
    module = request.app.state.registry["gmail"]
    assert isinstance(module, GmailModule)
    try:
        finish_oauth(_base_url(request), str(request.url))
        module.job.status = "idle"
        module.job.message = "Gmail connected (read-only). You can run an inbox skim."
        module.job.summary = ""
    except Exception as exc:  # noqa: BLE001
        module.job.status = "error"
        module.job.message = f"OAuth failed: {exc}"
    return RedirectResponse("/modules/gmail", status_code=303)
