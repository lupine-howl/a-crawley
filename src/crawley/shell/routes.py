"""Dashboard shell routes (Jinja2 + HTMX)."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urlparse
import os

from fastapi import APIRouter, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from crawley.bind import (
    guess_reachable_urls,
    host_exposes_lan,
    resolve_bind_host,
    resolve_bind_port,
)
from crawley.data.snapshots import get_snapshot
from crawley.day_brief import compose_day_brief_markdown, regenerate_day_brief_llm
from crawley.git_update import git_status, pull_latest, reload_enabled
from crawley.google_oauth import authorization_url, finish_oauth, google_auth_status
from crawley.jobs import JobState
from crawley.llm.factory import llm_status, test_llm_connection
from crawley.llm.models_catalog import ensure_model_in_options, list_openai_models
from crawley.markdown_render import render_markdown
from crawley.modules.calendar import CalendarModule
from crawley.modules.contract import Module
from crawley.modules.fitness import FitnessModule
from crawley.modules.gmail import GmailModule
from crawley.modules.investment import InvestmentModule
from crawley.modules.registry import nav_modules
from crawley.modules.work import WorkModule
from crawley.settings import (
    THEME_COOKIE,
    THEME_IDS,
    load_settings,
    resolve_theme,
    update_llm_settings,
    update_network_settings,
    update_prompt_settings,
    update_scale_settings,
    update_simulation_settings,
    update_theme_setting,
)
from crawley.shared_context import (
    list_pins,
    load_standing_notes,
    pin_history,
    save_standing_notes,
    unpin_history,
)
from crawley.writeback import read_audit_entries

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
    """Public base URL for OAuth redirects — preserve Tailscale/LAN Host headers."""
    url = str(request.base_url).rstrip("/")
    parsed = urlparse(url)
    host = parsed.hostname or "127.0.0.1"
    # Only rewrite the wildcard bind name; keep Tailscale/LAN hosts intact.
    if host == "0.0.0.0":
        host = "127.0.0.1"
    elif host == "localhost":
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
    sender = panel.get("sender") or {}
    profile_md = (sender.get("profile") or {}).get("markdown") or ""
    if profile_md:
        panel = {**panel, "profile_html": render_markdown(profile_md)}
    company = panel.get("company") or {}
    company_profile = (company.get("profile") or {}).get("markdown") or ""
    if company_profile:
        panel = {**panel, "profile_html": render_markdown(company_profile)}
    return panel


def _module_response(
    request: Request,
    module: Module,
    *,
    status_code: int = 200,
    panel: dict[str, Any] | None = None,
) -> HTMLResponse:
    registry: dict[str, Module] = request.app.state.registry
    ctx = _base_context(request, registry)
    ctx.update(
        {
            "active_id": module.meta.id,
            "module": module,
            "panel": _enrich_panel(panel if panel is not None else module.panel_context()),
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
    network_notice: str | None = None,
    update_result: dict | None = None,
    simulation_notice: str | None = None,
    scale_notice: str | None = None,
    history_notice: str | None = None,
    history_query: str = "",
    refresh_models: bool = False,
) -> dict[str, Any]:
    from crawley.data.snapshots import list_history

    registry: dict[str, Module] = request.app.state.registry
    settings = load_settings()
    catalog = list_openai_models(force_refresh=refresh_models)
    models = ensure_model_in_options(settings.llm.model, list(catalog["models"]))  # type: ignore[arg-type]
    bind_host = resolve_bind_host(lan_enabled=settings.network.lan_enabled)
    # Reflect what the *running* process would use after restart vs env override
    env_host = os.environ.get("CRAWLEY_HOST", "").strip()
    lan = host_exposes_lan(bind_host)
    gstat = git_status()
    history = list_history(query=history_query, limit=40)
    pins = list_pins()
    pin_ids = {p.get("id") for p in pins}
    for row in history:
        row["pinned"] = row.get("id") in pin_ids
    ctx = _base_context(request, registry)
    ctx.update(
        {
            "active_id": "settings",
            "themes": THEME_META,
            "llm_settings": settings.llm,
            "prompt_settings": settings.prompts,
            "scale_settings": settings.scale,
            "scale_notice": scale_notice,
            "network_settings": settings.network,
            "simulation_settings": settings.simulation,
            "bind_host": bind_host,
            "bind_port": resolve_bind_port(),
            "bind_exposes_lan": lan,
            "env_host_override": env_host or None,
            "has_stored_key": bool(settings.llm.api_key),
            "save_notice": save_notice,
            "prompts_notice": prompts_notice,
            "network_notice": network_notice,
            "simulation_notice": simulation_notice,
            "history_notice": history_notice,
            "history_query": history_query,
            "history_entries": history,
            "context_pins": pins,
            "test_result": test_result,
            "model_options": models,
            "models_error": catalog.get("error"),
            "models_source": catalog.get("source"),
            "audit_entries": read_audit_entries(limit=20),
            "git_status": gstat,
            "reload_enabled": reload_enabled(),
            "update_pull_allowed": bool(gstat.is_repo),
            "update_result": update_result,
            "reachable_urls": guess_reachable_urls(resolve_bind_port()) if lan else [],
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

    glance_ids = (
        "investment",
        "gmail",
        "calendar",
        "fitness",
        "co-parenting",
        "diy",
        "work",
        "finance-taxes",
        "coding-creative",
    )
    auth = google_auth_status()
    settings = load_settings()
    bind_host = resolve_bind_host(lan_enabled=settings.network.lan_enabled)
    include_shared = request.query_params.get("shared") == "1"
    brief = compose_day_brief_markdown(include_shared_context=include_shared)
    stored_brief = get_snapshot("day-brief")

    def md(snap):
        return render_markdown(snap.summary_md) if snap else None

    glance: dict[str, Any] = {}
    for mid in glance_ids:
        snap = get_snapshot(mid)
        key = mid.replace("-", "_")
        glance[f"{key}_snapshot"] = snap
        glance[f"{key}_html"] = md(snap)

    ctx.update(
        {
            **glance,
            "day_brief_markdown": (
                stored_brief.summary_md if stored_brief else brief["markdown"]
            ),
            "day_brief_html": render_markdown(
                stored_brief.summary_md if stored_brief else brief["markdown"]
            ),
            "day_brief_meta": brief,
            "day_brief_updated_at": stored_brief.updated_at if stored_brief else None,
            "standing_notes": load_standing_notes(),
            "google_auth": auth,
            "gmail_auth": auth,
            "lan_enabled": settings.network.lan_enabled,
            "bind_exposes_lan": host_exposes_lan(bind_host),
            "error": None,
        }
    )
    return templates.TemplateResponse(request, "dashboard.html", ctx)


@router.post("/day-brief/refresh", response_class=HTMLResponse)
def day_brief_refresh(
    request: Request,
    use_llm: str | None = Form(None),
    include_shared_context: str | None = Form(None),
) -> HTMLResponse:
    include_shared = include_shared_context == "on"
    if use_llm == "on":
        regenerate_day_brief_llm(include_shared_context=include_shared)
    else:
        brief = compose_day_brief_markdown(include_shared_context=include_shared)
        if not brief["empty"]:
            from crawley.data.snapshots import save_snapshot

            save_snapshot("day-brief", brief["markdown"])
    return RedirectResponse("/#day-brief", status_code=303)


@router.post("/standing-notes", response_class=HTMLResponse)
def standing_notes_save(request: Request, notes: str = Form("")) -> HTMLResponse:
    save_standing_notes(notes)
    return RedirectResponse("/#standing-notes", status_code=303)


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
    base_url: str = Form("http://127.0.0.1:11434"),
    timeout_s: str = Form("60"),
) -> HTMLResponse:
    try:
        timeout_val = float(timeout_s or "60")
    except ValueError:
        timeout_val = 60.0
    update_llm_settings(
        provider=provider,
        model=model,
        api_key=api_key,
        base_url=base_url,
        timeout_s=timeout_val,
    )
    ctx = _settings_context(
        request,
        save_notice="Settings saved. New requests use the updated LLM configuration.",
        refresh_models=provider == "openai",
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


@router.post("/settings/network", response_class=HTMLResponse)
def settings_network_save(
    request: Request,
    lan_enabled: str | None = Form(None),
) -> HTMLResponse:
    update_network_settings(lan_enabled=lan_enabled == "on")
    ctx = _settings_context(
        request,
        network_notice=(
            "Network preference saved. Restart Crawley for the bind address to change. "
            "Trusted LAN only — there is no login gate."
        ),
    )
    if request.headers.get("hx-request") == "true":
        return templates.TemplateResponse(request, "partials/settings_panel.html", ctx)
    return templates.TemplateResponse(request, "settings.html", ctx)


@router.post("/settings/simulation", response_class=HTMLResponse)
def settings_simulation_save(
    request: Request,
    starting_cash: str = Form("100000"),
    fee_flat: str = Form("10"),
    fee_pct: str = Form("0.1"),
    currency: str = Form("AUD"),
    broker_label: str = Form("Paper (simulation)"),
    reset_cash: str | None = Form(None),
) -> HTMLResponse:
    try:
        update_simulation_settings(
            starting_cash=float(starting_cash),
            fee_flat=float(fee_flat),
            fee_pct=float(fee_pct),
            currency=currency,
            broker_label=broker_label,
            reset_portfolio_cash=reset_cash == "on",
        )
        notice = "Simulation settings saved. These never enable live trading."
        if reset_cash == "on":
            notice += " Paper portfolio reset to starting cash."
    except ValueError:
        notice = "Could not parse simulation numbers."
    ctx = _settings_context(request, simulation_notice=notice)
    if request.headers.get("hx-request") == "true":
        return templates.TemplateResponse(request, "partials/settings_panel.html", ctx)
    return templates.TemplateResponse(request, "settings.html", ctx)


@router.post("/settings/scale", response_class=HTMLResponse)
def settings_scale_save(
    request: Request,
    inbox_cap: str = Form("100"),
    inbox_keep_max: str = Form("100"),
    asx_cap: str = Form("50"),
) -> HTMLResponse:
    try:
        update_scale_settings(
            inbox_cap=int(float(inbox_cap)),
            inbox_keep_max=int(float(inbox_keep_max)),
            asx_cap=int(float(asx_cap)),
        )
        notice = "Desk scale saved (hard ceiling 200). Retention prune applied."
    except ValueError:
        notice = "Could not parse scale numbers."
    ctx = _settings_context(request, scale_notice=notice)
    if request.headers.get("hx-request") == "true":
        return templates.TemplateResponse(request, "partials/settings_panel.html", ctx)
    return templates.TemplateResponse(request, "settings.html", ctx)


@router.get("/settings/history", response_class=HTMLResponse)
def settings_history(request: Request, q: str = "") -> HTMLResponse:
    ctx = _settings_context(request, history_query=q)
    if request.headers.get("hx-request") == "true":
        return templates.TemplateResponse(request, "partials/settings_panel.html", ctx)
    return templates.TemplateResponse(request, "settings.html", ctx)


@router.post("/settings/history/pin", response_class=HTMLResponse)
def settings_history_pin(request: Request, entry_id: str = Form("")) -> HTMLResponse:
    ok, msg = pin_history(entry_id)
    ctx = _settings_context(request, history_notice=msg)
    if request.headers.get("hx-request") == "true":
        return templates.TemplateResponse(request, "partials/settings_panel.html", ctx)
    return templates.TemplateResponse(request, "settings.html", ctx)


@router.post("/settings/history/unpin", response_class=HTMLResponse)
def settings_history_unpin(request: Request, entry_id: str = Form("")) -> HTMLResponse:
    unpin_history(entry_id)
    ctx = _settings_context(request, history_notice="Pin removed.")
    if request.headers.get("hx-request") == "true":
        return templates.TemplateResponse(request, "partials/settings_panel.html", ctx)
    return templates.TemplateResponse(request, "settings.html", ctx)


@router.post("/settings/update/pull", response_class=HTMLResponse)
def settings_update_pull(request: Request) -> HTMLResponse:
    settings = load_settings()
    bind_host = resolve_bind_host(lan_enabled=settings.network.lan_enabled)
    result = pull_latest(lan_bound=host_exposes_lan(bind_host))
    update_result = {
        "ok": result.ok,
        "state": result.state,
        "message": result.message,
        "branch": result.branch,
        "before_sha": result.before_sha,
        "after_sha": result.after_sha,
        "changed_watched": result.changed_watched,
        "reload_enabled": result.reload_enabled,
        "lan_warn": result.lan_warn,
    }
    ctx = _settings_context(request, update_result=update_result)
    if request.headers.get("hx-request") == "true":
        return templates.TemplateResponse(request, "partials/settings_panel.html", ctx)
    return templates.TemplateResponse(request, "settings.html", ctx)


@router.post("/settings/prompts", response_class=HTMLResponse)
async def settings_prompts_save(request: Request) -> HTMLResponse:
    form = await request.form()
    fields = {str(k): str(v) for k, v in form.items() if isinstance(v, str)}
    update_prompt_settings(**fields)
    ctx = _settings_context(
        request,
        prompts_notice="Prompts saved. The next module run will use them.",
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
def investment_run(
    request: Request,
    query: str = Form("US stock market outlook"),
    use_cache: str | None = Form(None),
) -> HTMLResponse:
    registry: dict[str, Module] = request.app.state.registry
    module = registry["investment"]
    assert isinstance(module, InvestmentModule)
    result = module.run({"query": query, "use_cache": use_cache == "on"})
    if result.error and module.job.status != "busy":
        module.job.status = "error"
        module.job.message = result.error
    return _module_response(request, module)


@router.get("/modules/investment/status", response_class=HTMLResponse)
def investment_status(request: Request) -> HTMLResponse:
    module = request.app.state.registry["investment"]
    return _module_response(request, module)


@router.post("/modules/investment/asx/start", response_class=HTMLResponse)
def asx_scan_start(request: Request) -> HTMLResponse:
    from crawley.asx_desk.worker import start_scan

    module = request.app.state.registry["investment"]
    assert isinstance(module, InvestmentModule)
    ok, msg = start_scan(request.app.state.executor)
    if not ok:
        module.job = JobState(status="error", message=msg)
    return _module_response(request, module)


@router.post("/modules/investment/asx/pause", response_class=HTMLResponse)
def asx_scan_pause(request: Request) -> HTMLResponse:
    from crawley.asx_desk.worker import request_pause

    module = request.app.state.registry["investment"]
    request_pause()
    return _module_response(request, module)


@router.post("/modules/investment/asx/resume", response_class=HTMLResponse)
def asx_scan_resume(request: Request) -> HTMLResponse:
    from crawley.asx_desk.worker import resume_scan

    module = request.app.state.registry["investment"]
    assert isinstance(module, InvestmentModule)
    ok, msg = resume_scan(request.app.state.executor)
    if not ok:
        module.job = JobState(status="error", message=msg)
    return _module_response(request, module)


@router.post("/modules/investment/asx/reset", response_class=HTMLResponse)
def asx_scan_reset(request: Request) -> HTMLResponse:
    from crawley.asx_desk.store import reset_poc_data
    from crawley.asx_desk.worker import request_pause

    module = request.app.state.registry["investment"]
    request_pause()
    reset_poc_data()
    return _module_response(request, module)


@router.post("/modules/investment/asx/poc-set", response_class=HTMLResponse)
def asx_poc_set(request: Request, tickers: str = Form("")) -> HTMLResponse:
    from crawley.asx_desk.store import set_poc_tickers

    module = request.app.state.registry["investment"]
    parts = [p.strip().upper() for p in tickers.replace(";", ",").split(",") if p.strip()]
    set_poc_tickers(parts)
    return _module_response(request, module)


@router.post("/modules/investment/asx/cap", response_class=HTMLResponse)
def asx_active_cap(request: Request, cap: str = Form("50")) -> HTMLResponse:
    from crawley.asx_desk.store import sync_active_cap
    from crawley.settings import update_scale_settings, load_settings

    module = request.app.state.registry["investment"]
    assert isinstance(module, InvestmentModule)
    try:
        n = int(float(cap))
    except ValueError:
        n = 50
    settings = load_settings()
    update_scale_settings(
        inbox_cap=settings.scale.inbox_cap,
        inbox_keep_max=settings.scale.inbox_keep_max,
        asx_cap=n,
    )
    sync_active_cap(n, expand_from_universe=True)
    return _module_response(request, module)


@router.post("/modules/investment/asx/sources/{source_id}/toggle", response_class=HTMLResponse)
def asx_source_toggle(
    request: Request,
    source_id: str,
    enabled: str | None = Form(None),
) -> HTMLResponse:
    from crawley.asx_desk.sources import set_source_enabled

    module = request.app.state.registry["investment"]
    set_source_enabled(source_id, enabled == "on")
    return _module_response(request, module)


@router.post("/modules/investment/asx/prompts", response_class=HTMLResponse)
def asx_prompts_save(
    request: Request,
    scan_system: str = Form(""),
    profile_system: str = Form(""),
    sentiment_system: str = Form(""),
) -> HTMLResponse:
    from crawley.asx_desk.sources import update_prompts

    module = request.app.state.registry["investment"]
    update_prompts(
        scan_system=scan_system,
        profile_system=profile_system,
        sentiment_system=sentiment_system,
    )
    return _module_response(request, module)


@router.get("/modules/investment/companies/{ticker}", response_class=HTMLResponse)
def asx_company_detail(request: Request, ticker: str) -> HTMLResponse:
    module = request.app.state.registry["investment"]
    assert isinstance(module, InvestmentModule)
    panel = module.company_panel_context(ticker)
    if panel is None:
        return _module_response(request, module, status_code=404)
    return _module_response(request, module, panel=panel)


@router.post("/modules/investment/companies/{ticker}/profile/retry", response_class=HTMLResponse)
def asx_company_profile_retry(request: Request, ticker: str) -> HTMLResponse:
    from crawley.asx_desk.worker import regenerate_profile

    module = request.app.state.registry["investment"]
    assert isinstance(module, InvestmentModule)
    regenerate_profile(ticker, request.app.state.executor)
    panel = module.company_panel_context(ticker)
    if panel is None:
        return _module_response(request, module, status_code=404)
    return _module_response(request, module, panel=panel)


@router.get("/modules/investment/recommendations", response_class=HTMLResponse)
def asx_recommendations(request: Request) -> HTMLResponse:
    module = request.app.state.registry["investment"]
    assert isinstance(module, InvestmentModule)
    return _module_response(request, module, panel=module.recommendations_panel_context())


@router.post("/modules/investment/recommendations/refresh", response_class=HTMLResponse)
def asx_recommendations_refresh(request: Request) -> HTMLResponse:
    from crawley.asx_desk.worker import refresh_recommendations

    module = request.app.state.registry["investment"]
    assert isinstance(module, InvestmentModule)
    ok, msg = refresh_recommendations(request.app.state.executor)
    if not ok:
        module.job = JobState(status="error", message=msg)
    return _module_response(request, module, panel=module.recommendations_panel_context())


@router.get("/modules/investment/portfolio", response_class=HTMLResponse)
def asx_portfolio(request: Request) -> HTMLResponse:
    module = request.app.state.registry["investment"]
    assert isinstance(module, InvestmentModule)
    return _module_response(request, module, panel=module.portfolio_panel_context())


@router.post("/modules/investment/portfolio/trade", response_class=HTMLResponse)
def asx_portfolio_trade(
    request: Request,
    ticker: str = Form(""),
    side: str = Form("buy"),
    qty: str = Form("10"),
    price: str = Form(""),
    note: str = Form(""),
    from_recs: str | None = Form(None),
) -> HTMLResponse:
    from crawley.asx_desk.portfolio import add_paper_trade

    module = request.app.state.registry["investment"]
    assert isinstance(module, InvestmentModule)
    price_val = None
    if price.strip():
        try:
            price_val = float(price)
        except ValueError:
            panel = module.portfolio_panel_context()
            panel["trade_ok"] = False
            panel["trade_notice"] = "Price must be a number."
            return _module_response(request, module, panel=panel)
    ok, msg, _ = add_paper_trade(
        ticker=ticker,
        side=side,
        qty=qty,
        price=price_val,
        note=note,
    )
    # From recommendations: stay on that list if the trade failed; otherwise show portfolio.
    if from_recs == "1" and not ok:
        panel = module.recommendations_panel_context()
    else:
        panel = module.portfolio_panel_context()
    panel["trade_ok"] = ok
    panel["trade_notice"] = msg
    return _module_response(request, module, panel=panel)


@router.post("/modules/investment/portfolio/reset", response_class=HTMLResponse)
def asx_portfolio_reset(request: Request) -> HTMLResponse:
    from crawley.asx_desk.portfolio import reset_portfolio

    module = request.app.state.registry["investment"]
    assert isinstance(module, InvestmentModule)
    reset_portfolio()
    return _module_response(request, module, panel=module.portfolio_panel_context())


@router.get("/modules/investment/events", response_class=HTMLResponse)
def asx_events(request: Request) -> HTMLResponse:
    module = request.app.state.registry["investment"]
    assert isinstance(module, InvestmentModule)
    return _module_response(request, module, panel=module.events_panel_context())


@router.post("/modules/investment/events/refresh", response_class=HTMLResponse)
def asx_events_refresh(request: Request) -> HTMLResponse:
    from crawley.asx_desk.worker import refresh_events

    module = request.app.state.registry["investment"]
    assert isinstance(module, InvestmentModule)
    ok, msg = refresh_events(request.app.state.executor)
    if not ok:
        module.job = JobState(status="error", message=msg)
    return _module_response(request, module, panel=module.events_panel_context())


@router.get("/modules/investment/bridge", response_class=HTMLResponse)
def asx_bridge(request: Request) -> HTMLResponse:
    module = request.app.state.registry["investment"]
    assert isinstance(module, InvestmentModule)
    return _module_response(request, module, panel=module.bridge_panel_context())


@router.post("/modules/investment/bridge/refresh", response_class=HTMLResponse)
def asx_bridge_refresh(request: Request) -> HTMLResponse:
    from crawley.bridge.matcher import run_bridge_scan

    module = request.app.state.registry["investment"]
    assert isinstance(module, InvestmentModule)
    try:
        run_bridge_scan()
    except Exception as exc:  # noqa: BLE001
        module.job = JobState(status="error", message=str(exc)[:300])
    return _module_response(request, module, panel=module.bridge_panel_context())


@router.get("/modules/gmail", response_class=HTMLResponse)
def gmail_panel(
    request: Request,
    q: str = "",
    category: str = "",
    todo: str = "",
) -> HTMLResponse:
    module = request.app.state.registry["gmail"]
    assert isinstance(module, GmailModule)
    return _module_response(
        request,
        module,
        panel=module.panel_context(query=q, category=category, todo=todo),
    )


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
def gmail_status(
    request: Request,
    q: str = "",
    category: str = "",
    todo: str = "",
) -> HTMLResponse:
    module = request.app.state.registry["gmail"]
    assert isinstance(module, GmailModule)
    return _module_response(
        request,
        module,
        panel=module.panel_context(query=q, category=category, todo=todo),
    )


@router.post("/modules/gmail/inbox/start", response_class=HTMLResponse)
def gmail_inbox_start(request: Request) -> HTMLResponse:
    from crawley.sender_inbox.worker import start_ingest

    module = request.app.state.registry["gmail"]
    assert isinstance(module, GmailModule)
    ok, msg = start_ingest(request.app.state.executor)
    if not ok:
        module.job = JobState(status="error", message=msg)
    return _module_response(request, module)


@router.post("/modules/gmail/inbox/pause", response_class=HTMLResponse)
def gmail_inbox_pause(request: Request) -> HTMLResponse:
    from crawley.sender_inbox.worker import request_pause

    module = request.app.state.registry["gmail"]
    request_pause()
    return _module_response(request, module)


@router.post("/modules/gmail/inbox/resume", response_class=HTMLResponse)
def gmail_inbox_resume(request: Request) -> HTMLResponse:
    from crawley.sender_inbox.worker import resume_ingest

    module = request.app.state.registry["gmail"]
    assert isinstance(module, GmailModule)
    ok, msg = resume_ingest(request.app.state.executor)
    if not ok:
        module.job = JobState(status="error", message=msg)
    return _module_response(request, module)


@router.post("/modules/gmail/inbox/reset", response_class=HTMLResponse)
def gmail_inbox_reset(request: Request) -> HTMLResponse:
    from crawley.sender_inbox.store import reset_poc_data
    from crawley.sender_inbox.worker import request_pause

    module = request.app.state.registry["gmail"]
    request_pause()
    reset_poc_data()
    return _module_response(request, module)


@router.get("/modules/gmail/senders/{sender_id}", response_class=HTMLResponse)
def gmail_sender_detail(request: Request, sender_id: str) -> HTMLResponse:
    module = request.app.state.registry["gmail"]
    assert isinstance(module, GmailModule)
    panel = module.sender_panel_context(sender_id)
    if panel is None:
        return _module_response(request, module, status_code=404)
    return _module_response(request, module, panel=panel)


@router.post("/modules/gmail/senders/{sender_id}/profile/retry", response_class=HTMLResponse)
def gmail_sender_profile_retry(request: Request, sender_id: str) -> HTMLResponse:
    from crawley.sender_inbox.worker import regenerate_profile

    module = request.app.state.registry["gmail"]
    assert isinstance(module, GmailModule)
    regenerate_profile(sender_id, request.app.state.executor)
    panel = module.sender_panel_context(sender_id)
    if panel is None:
        return _module_response(request, module, status_code=404)
    return _module_response(request, module, panel=panel)


@router.post("/modules/gmail/todos/{todo_id}/toggle", response_class=HTMLResponse)
def gmail_todo_toggle(request: Request, todo_id: str) -> HTMLResponse:
    from crawley.sender_inbox.store import toggle_todo

    module = request.app.state.registry["gmail"]
    assert isinstance(module, GmailModule)
    todo = toggle_todo(todo_id)
    if todo is None:
        return _module_response(request, module, status_code=404)
    panel = module.sender_panel_context(todo["sender_id"])
    if panel is None:
        return _module_response(request, module)
    return _module_response(request, module, panel=panel)


@router.post("/modules/calendar/run", response_class=HTMLResponse)
def calendar_run(request: Request) -> HTMLResponse:
    module = request.app.state.registry["calendar"]
    assert isinstance(module, CalendarModule)
    result = module.run({})
    if result.error and module.job.status != "busy":
        module.job.status = "error"
        module.job.message = result.error
    return _module_response(request, module)


@router.get("/modules/calendar/status", response_class=HTMLResponse)
def calendar_status(request: Request) -> HTMLResponse:
    module = request.app.state.registry["calendar"]
    return _module_response(request, module)


@router.post("/modules/fitness/run", response_class=HTMLResponse)
def fitness_run(
    request: Request,
    goal: str = Form(""),
    use_import: str | None = Form(None),
) -> HTMLResponse:
    module = request.app.state.registry["fitness"]
    assert isinstance(module, FitnessModule)
    result = module.run({"goal": goal, "use_import": use_import == "on"})
    if result.error and module.job.status != "busy":
        module.job.status = "error"
        module.job.message = result.error
    return _module_response(request, module)


@router.get("/modules/fitness/status", response_class=HTMLResponse)
def fitness_status(request: Request) -> HTMLResponse:
    module = request.app.state.registry["fitness"]
    return _module_response(request, module)


@router.post("/modules/fitness/import", response_class=HTMLResponse)
async def fitness_import(request: Request) -> HTMLResponse:
    from crawley.modules.fitness_import import save_activity_import

    module = request.app.state.registry["fitness"]
    form = await request.form()
    upload = form.get("file")
    raw = b""
    filename = ""
    if upload is not None and hasattr(upload, "read"):
        raw = await upload.read()  # type: ignore[misc]
        filename = getattr(upload, "filename", "") or ""
    ok, msg = save_activity_import(raw, filename=filename)
    panel = module.panel_context()
    panel["import_ok"] = ok
    panel["import_notice"] = msg
    return _module_response(request, module, panel=panel)


@router.post("/modules/fitness/import/clear", response_class=HTMLResponse)
def fitness_import_clear(request: Request) -> HTMLResponse:
    from crawley.modules.fitness_import import clear_activity_import

    module = request.app.state.registry["fitness"]
    clear_activity_import()
    panel = module.panel_context()
    panel["import_ok"] = True
    panel["import_notice"] = "Import cleared."
    return _module_response(request, module, panel=panel)


@router.post("/modules/work/save", response_class=HTMLResponse)
def work_save(request: Request, notes: str = Form("")) -> HTMLResponse:
    module = request.app.state.registry["work"]
    assert isinstance(module, WorkModule)
    result = module.save_only(notes)
    if result.error:
        module.job.status = "error"
        module.job.message = result.error
    return _module_response(request, module)


@router.post("/modules/work/run", response_class=HTMLResponse)
def work_run(request: Request, notes: str = Form("")) -> HTMLResponse:
    module = request.app.state.registry["work"]
    assert isinstance(module, WorkModule)
    result = module.run({"notes": notes})
    if result.error and module.job.status != "busy":
        module.job.status = "error"
        module.job.message = result.error
    return _module_response(request, module)


@router.get("/modules/work/status", response_class=HTMLResponse)
def work_status(request: Request) -> HTMLResponse:
    module = request.app.state.registry["work"]
    return _module_response(request, module)


def _notes_module_save(request: Request, module_id: str, notes: str) -> HTMLResponse:
    module = request.app.state.registry[module_id]
    result = module.save_only(notes)  # type: ignore[attr-defined]
    if result.error:
        module.job.status = "error"  # type: ignore[attr-defined]
        module.job.message = result.error  # type: ignore[attr-defined]
    return _module_response(request, module)


def _notes_module_run(
    request: Request,
    module_id: str,
    notes: str,
    *,
    include_shared_context: bool = False,
) -> HTMLResponse:
    module = request.app.state.registry[module_id]
    payload: dict[str, Any] = {"notes": notes}
    if include_shared_context:
        payload["include_shared_context"] = True
    result = module.run(payload)
    if result.error and getattr(module, "job", None) is not None and module.job.status != "busy":
        module.job.status = "error"
        module.job.message = result.error
    return _module_response(request, module)


@router.post("/modules/co-parenting/save", response_class=HTMLResponse)
def co_parenting_save(request: Request, notes: str = Form("")) -> HTMLResponse:
    return _notes_module_save(request, "co-parenting", notes)


@router.post("/modules/co-parenting/run", response_class=HTMLResponse)
def co_parenting_run(request: Request, notes: str = Form("")) -> HTMLResponse:
    return _notes_module_run(request, "co-parenting", notes)


@router.get("/modules/co-parenting/status", response_class=HTMLResponse)
def co_parenting_status(request: Request) -> HTMLResponse:
    return _module_response(request, request.app.state.registry["co-parenting"])


@router.post("/modules/diy/save", response_class=HTMLResponse)
def diy_save(request: Request, notes: str = Form("")) -> HTMLResponse:
    return _notes_module_save(request, "diy", notes)


@router.post("/modules/diy/run", response_class=HTMLResponse)
def diy_run(request: Request, notes: str = Form("")) -> HTMLResponse:
    return _notes_module_run(request, "diy", notes)


@router.get("/modules/diy/status", response_class=HTMLResponse)
def diy_status(request: Request) -> HTMLResponse:
    return _module_response(request, request.app.state.registry["diy"])


@router.post("/modules/finance-taxes/save", response_class=HTMLResponse)
def finance_save(request: Request, notes: str = Form("")) -> HTMLResponse:
    return _notes_module_save(request, "finance-taxes", notes)


@router.post("/modules/finance-taxes/run", response_class=HTMLResponse)
def finance_run(request: Request, notes: str = Form("")) -> HTMLResponse:
    return _notes_module_run(request, "finance-taxes", notes)


@router.get("/modules/finance-taxes/status", response_class=HTMLResponse)
def finance_status(request: Request) -> HTMLResponse:
    return _module_response(request, request.app.state.registry["finance-taxes"])


@router.post("/modules/coding-creative/save", response_class=HTMLResponse)
def coding_save(request: Request, notes: str = Form("")) -> HTMLResponse:
    return _notes_module_save(request, "coding-creative", notes)


@router.post("/modules/coding-creative/run", response_class=HTMLResponse)
def coding_run(
    request: Request,
    notes: str = Form(""),
    include_shared_context: str | None = Form(None),
) -> HTMLResponse:
    return _notes_module_run(
        request,
        "coding-creative",
        notes,
        include_shared_context=include_shared_context == "on",
    )


@router.get("/modules/coding-creative/status", response_class=HTMLResponse)
def coding_status(request: Request) -> HTMLResponse:
    return _module_response(request, request.app.state.registry["coding-creative"])


@router.post("/modules/calendar/write-back/propose", response_class=HTMLResponse)
def calendar_write_propose(
    request: Request,
    summary: str = Form(""),
    start: str = Form(""),
    end: str = Form(""),
    description: str = Form(""),
) -> HTMLResponse:
    module = request.app.state.registry["calendar"]
    assert isinstance(module, CalendarModule)
    result = module.write_back(
        {
            "action": "propose",
            "summary": summary,
            "start": start,
            "end": end,
            "description": description,
        }
    )
    if result.error:
        module.job = JobState(status="error", message=result.error)
    return _module_response(request, module)


@router.post("/modules/calendar/write-back/confirm", response_class=HTMLResponse)
def calendar_write_confirm(
    request: Request,
    draft_id: str = Form(""),
) -> HTMLResponse:
    module = request.app.state.registry["calendar"]
    assert isinstance(module, CalendarModule)
    result = module.write_back({"action": "confirm", "draft_id": draft_id})
    if result.error:
        module.job = JobState(status="error", message=result.error)
    return _module_response(request, module)


@router.post("/modules/calendar/write-back/cancel", response_class=HTMLResponse)
def calendar_write_cancel(
    request: Request,
    draft_id: str = Form(""),
) -> HTMLResponse:
    module = request.app.state.registry["calendar"]
    assert isinstance(module, CalendarModule)
    result = module.cancel_write_back(draft_id)
    if result.error:
        module.job = JobState(status="error", message=result.error)
    return _module_response(request, module)


@router.post("/modules/{module_id}/write-back/dry-run", response_class=HTMLResponse)
def module_write_back_dry_run(
    request: Request,
    module_id: str,
    action: str = Form("preview"),
) -> HTMLResponse:
    """Exercise ADR-006 dry-run hook (no remote mutation)."""
    registry: dict[str, Module] = request.app.state.registry
    module = registry.get(module_id)
    if module is None:
        return HTMLResponse("Unknown module", status_code=404)
    payload_action = "dry_run" if isinstance(module, CalendarModule) else action
    result = module.write_back({"action": payload_action, "source": "settings_or_panel"})
    if isinstance(module, (GmailModule, CalendarModule)) and hasattr(module, "job"):
        if result.error:
            module.job = JobState(status="error", message=result.error)
        else:
            module.job = JobState(
                status="idle",
                message=result.summary or "Dry-run recorded.",
                details=result.details,
            )
    return _module_response(request, module)


@router.get("/modules/gmail/oauth/start")
def gmail_oauth_start(request: Request) -> RedirectResponse:
    module = request.app.state.registry["gmail"]
    assert isinstance(module, GmailModule)
    include_write = request.query_params.get("calendar_write") == "1"
    try:
        url, state = authorization_url(
            _base_url(request),
            include_calendar_write=include_write,
        )
        module.oauth_state = state
        return RedirectResponse(url)
    except Exception as exc:  # noqa: BLE001
        module.job = JobState(status="error", message=str(exc))
        return RedirectResponse("/modules/gmail", status_code=303)


@router.get("/modules/gmail/oauth/callback")
def gmail_oauth_callback(request: Request) -> RedirectResponse:
    module = request.app.state.registry["gmail"]
    assert isinstance(module, GmailModule)
    calendar = request.app.state.registry.get("calendar")
    try:
        finish_oauth(_base_url(request), str(request.url))
        msg = (
            "Google connected (Gmail + Calendar read-only). "
            "You can skim inbox or upcoming events."
        )
        module.job.status = "idle"
        module.job.message = msg
        module.job.summary = ""
        if isinstance(calendar, CalendarModule):
            calendar.job.status = "idle"
            calendar.job.message = msg
            calendar.job.summary = ""
        # Optional ?next= module redirect
        next_path = request.query_params.get("next") or "/modules/gmail"
        if next_path not in {"/modules/gmail", "/modules/calendar"}:
            next_path = "/modules/gmail"
        return RedirectResponse(next_path, status_code=303)
    except Exception as exc:  # noqa: BLE001
        module.job.status = "error"
        module.job.message = f"OAuth failed: {exc}"
        return RedirectResponse("/modules/gmail", status_code=303)
