"""FastAPI application factory."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI

from crawley.data.duck import init_schema
from crawley.data.paths import ensure_data_dirs
from crawley.modules.calendar import CalendarModule
from crawley.modules.coding_creative import CodingCreativeModule
from crawley.modules.co_parenting import CoParentingModule
from crawley.modules.diy import DiyModule
from crawley.modules.finance import FinanceModule
from crawley.modules.fitness import FitnessModule
from crawley.modules.gmail import GmailModule
from crawley.modules.investment import InvestmentModule
from crawley.modules.registry import build_registry
from crawley.modules.work import WorkModule
from crawley.api.asx_extra import router as asx_extra_router
from crawley.api.gmail_routes import router as gmail_api_router
from crawley.api.routes import router as api_router
from crawley.api.settings_routes import router as settings_api_router
from crawley.shell.routes import router as shell_router

ROOT = Path(__file__).resolve().parents[2]

_LIVE_WITH_EXECUTOR = (
    InvestmentModule,
    GmailModule,
    CalendarModule,
    FitnessModule,
    WorkModule,
    CoParentingModule,
    DiyModule,
    FinanceModule,
    CodingCreativeModule,
)


def create_app() -> FastAPI:
    load_dotenv(ROOT / ".env")
    ensure_data_dirs()
    init_schema()

    executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="crawley")
    registry = build_registry()
    for module in registry.values():
        if isinstance(module, _LIVE_WITH_EXECUTOR):
            module.bind_executor(executor)
        module.startup()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield
        executor.shutdown(wait=False, cancel_futures=True)
        for module in registry.values():
            module.shutdown()

    app = FastAPI(
        title="Crawley analytics",
        version="0.1.0",
        description=(
            "Local-first analytics API for crawley-ui (Phone Preview). "
            "Product UI is not Jinja/HTMX — see docs/migration-phone-preview.md."
        ),
        lifespan=lifespan,
    )
    app.state.registry = registry
    app.state.executor = executor
    app.include_router(api_router)
    app.include_router(asx_extra_router)
    app.include_router(gmail_api_router)
    app.include_router(settings_api_router)
    app.include_router(shell_router)
    return app
