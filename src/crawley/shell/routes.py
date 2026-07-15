"""Dashboard shell routes (Jinja2 + HTMX)."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from fastapi import APIRouter, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from crawley.data.snapshots import get_snapshot
from crawley.jobs import JobState
from crawley.llm.factory import llm_status, test_llm_connection
from crawley.llm.models_catalog import ensure_model_in_options, list_openai_models
from crawley.markdown_render import render_markdown
from crawley.modules.contract import Module
from crawley.modules.gmail import GmailModule, authorization_url, finish_oauth
from crawley.modules.investment import InvestmentModule
from crawley.modules.registry import nav_modules
from crawley.settings import (
    THEME_COOKIE,
    THEME_IDS,
    load_settings,
    resolve_theme,
    update_llm_settings,
    update_prompt_settings,
    update_theme_setting,
)

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

router = APIRouter()

THEME_META = (
    {"id": "paper", "label": "Paper", "swatch_bg": "#f6f3ee", "swatch_accent": "#0f766e"},
    {"id": "slate", "label": "Slate", "swatch_bg": "#eef2f6", "swatch_accent": "#0e7490"},
    {"id": "ink", "label": "Ink", "swatch_bg": "#0c0f14", "swatch_accent": "#2dd4bf"},
    {"id": "moss", "label": "Moss", "swatch_bg": "#101612", "swatch_accent": "#6b9f6e"},
)


def _base_url(request: Request) -> str:
    url = str(request.base_url).rstrip("/")
    parsed = urlparse(url)
    host = parsed.hostname or "127.0.0.1"
    if host in {"0.0.0.0", "localhost"}:
        host = "127.0.0.1"
    port = parsed.port
    netloc = f"{host}:{port}" if port else host
    return f"{parsed.scheme}://{netloc}"


def _theme_for_request(request: Request) -> str:
    return resolve_theme(cookie_value=request.cookies.get(THEME_COOKIE))


def _theme_label(theme_id: str) -> str:
    for item in THEME_META:
        if item["id"] == theme_id:
            return item["label"]
    return theme_id.title()


def _base_context(request: Request, registry: dict[str, Module]) -> dict[str, Any]:
    theme = _theme_for_request(request)
    return {
        "request": request,
        "nav": nav_modules(registry),
        "llm": llm_status(),
        "theme": theme,
        "theme_label": _theme_label(theme),
    }


def _enrich_panel(panel: dict[str, Any]) -> dict[str, Any]:
    job = panel.get("job") or {}
    summary = job.get("summary") or ""
    if summary:
        panel = {**panel, "summary_html": render_markdown(summary)}
    return panel


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
            "panel": _enrich_panel(module.panel_context()),
        }
    )
    template = "partials/panel.html" if request.headers.get("hx-request") == "true" else "module.html"
    return templates.TemplateResponse(request, template, ctx, status_code=status_code)


def _settings_context(
    request: Request,
    *,
    save_notice: str | None = None,
    test_result: dict | None = None,
    prompts_notice: str | None = None,
    refresh_models: bool = False,
) -> dict[str, Any]:
    registry: dict[str, Module] = request.app.state.registry
    settings = load_settings()
    catalog = list_openai_models(force_refresh=refresh_models)
    models = ensure_model_in_options(settings.llm.model, list(catalog["models"]))  # type: ignore[arg-type]
    ctx = _base_context(request, registry)
    ctx.update(
        {
            "active_id": "settings",
            "themes": THEME_META,
            "llm_settings": settings.llm,
            "prompt_settings": settings.prompts,
            "has_stored_key": bool(settings.llm.api_key),
            "save_notice": save_notice,
            "prompts_notice": prompts_notice,
            "test_result": test_result,
            "model_options": models,
            "models_error": catalog.get("error"),
            "models_source": catalog.get("source"),
        }
    )
    return ctx


def _set_theme_cookie(response: Response, theme: str) -> None:
    response.set_cookie(
        THEME_COOKIE,
        theme,
        max_age=60 * 60 * 24 * 365,
        httponly=False,
        samesite="lax",
        path="/",
    )


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request) -> HTMLResponse:
    registry: dict[str, Module] = request.app.state.registry
    ctx = _base_context(request, registry)
    ctx["active_id"] = None

    inv = get_snapshot("investment")
    gmail = get_snapshot("gmail")
    gmail_module = registry.get("gmail")
    auth = gmail_module.auth_status() if isinstance(gmail_module, GmailModule) else {}

    ctx.update(
        {
            "investment_snapshot": inv,
            "investment_html": render_markdown(inv.summary_md) if inv else None,
            "gmail_snapshot": gmail,
            "gmail_html": render_markdown(gmail.summary_md) if gmail else None,
            "gmail_auth": auth,
            "error": None,
        }
    )
    return templates.TemplateResponse(request, "dashboard.html", ctx)


@router.get("/settings", response_class=HTMLResponse)
def settings_page(request: Request) -> HTMLResponse:
    ctx = _settings_context(request)
    if request.headers.get("hx-request") == "true":
        return templates.TemplateResponse(request, "partials/settings_panel.html", ctx)
    return templates.TemplateResponse(request, "settings.html", ctx)


@router.post("/settings/theme")
def settings_theme(request: Request, theme: str = Form("paper")) -> Response:
    chosen = theme if theme in THEME_IDS else "paper"
    update_theme_setting(chosen)
    # Full refresh so data-theme on <html> updates across chrome.
    response = Response(status_code=200)
    response.headers["HX-Refresh"] = "true"
    _set_theme_cookie(response, chosen)
    # Non-HTMX fallback
    if request.headers.get("hx-request") != "true":
        redirect = RedirectResponse("/settings", status_code=303)
        _set_theme_cookie(redirect, chosen)
        return redirect
    return response


@router.post("/settings/llm", response_class=HTMLResponse)
def settings_llm_save(
    request: Request,
    provider: str = Form("openai"),
    model: str = Form("gpt-4o-mini"),
    api_key: str = Form(""),
) -> HTMLResponse:
    update_llm_settings(provider=provider, model=model, api_key=api_key)
    ctx = _settings_context(
        request,
        save_notice="Settings saved. New requests use the updated LLM configuration.",
        refresh_models=True,
    )
    if request.headers.get("hx-request") == "true":
        return templates.TemplateResponse(request, "partials/settings_panel.html", ctx)
    return templates.TemplateResponse(request, "settings.html", ctx)


@router.post("/settings/llm/models/refresh", response_class=HTMLResponse)
def settings_models_refresh(request: Request) -> HTMLResponse:
    ctx = _settings_context(request, refresh_models=True)
    if request.headers.get("hx-request") == "true":
        return templates.TemplateResponse(request, "partials/settings_panel.html", ctx)
    return templates.TemplateResponse(request, "settings.html", ctx)


@router.post("/settings/prompts", response_class=HTMLResponse)
def settings_prompts_save(
    request: Request,
    investment_system: str = Form(""),
    investment_user_footer: str = Form(""),
    gmail_system: str = Form(""),
    gmail_user_header: str = Form(""),
) -> HTMLResponse:
    update_prompt_settings(
        investment_system=investment_system,
        investment_user_footer=investment_user_footer,
        gmail_system=gmail_system,
        gmail_user_header=gmail_user_header,
    )
    ctx = _settings_context(
        request,
        prompts_notice="Prompts saved. The next Investment / Gmail run will use them.",
    )
    if request.headers.get("hx-request") == "true":
        return templates.TemplateResponse(request, "partials/settings_panel.html", ctx)
    return templates.TemplateResponse(request, "settings.html", ctx)


@router.post("/settings/llm/test", response_class=HTMLResponse)
def settings_llm_test(request: Request) -> HTMLResponse:
    result = test_llm_connection()
    return templates.TemplateResponse(
        request,
        "partials/test_result.html",
        {"request": request, "test_result": result},
    )


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
