"""FastAPI application factory — analytics JSON API + OAuth (no Jinja product UI)."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI

from crawley.api.asx_extra import router as asx_extra_router
from crawley.api.gmail_routes import router as gmail_api_router
from crawley.api.oauth_routes import router as oauth_router
from crawley.api.routes import router as api_router
from crawley.api.settings_routes import router as settings_api_router
from crawley.data.duck import init_schema
from crawley.data.paths import ensure_data_dirs

ROOT = Path(__file__).resolve().parents[2]


def create_app() -> FastAPI:
    load_dotenv(ROOT / ".env")
    ensure_data_dirs()
    init_schema()

    executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="crawley")

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield
        executor.shutdown(wait=False, cancel_futures=True)

    app = FastAPI(
        title="Crawley analytics",
        version="0.1.0",
        description=(
            "Local-first analytics API for crawley-ui (Phone Preview). "
            "Product UI is crawley-ui — Jinja/HTMX shell removed (Sprint 35). "
            "See docs/migration-phone-preview.md."
        ),
        lifespan=lifespan,
    )
    # Executor for in-process ASX/Gmail workers when not using external daemons.
    app.state.executor = executor
    app.state.registry = {}  # Product modules unloaded; brains live under asx_desk / sender_inbox

    app.include_router(api_router)
    app.include_router(asx_extra_router)
    app.include_router(gmail_api_router)
    app.include_router(settings_api_router)
    app.include_router(oauth_router)
    return app
