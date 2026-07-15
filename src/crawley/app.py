"""FastAPI application factory."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI

from crawley.data.duck import init_schema
from crawley.data.paths import ensure_data_dirs
from crawley.modules.gmail import GmailModule
from crawley.modules.investment import InvestmentModule
from crawley.modules.registry import build_registry
from crawley.shell.routes import router as shell_router

ROOT = Path(__file__).resolve().parents[2]


def create_app() -> FastAPI:
    load_dotenv(ROOT / ".env")
    ensure_data_dirs()
    init_schema()

    executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="crawley")
    registry = build_registry()
    for module in registry.values():
        if isinstance(module, (InvestmentModule, GmailModule)):
            module.bind_executor(executor)
        module.startup()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield
        executor.shutdown(wait=False, cancel_futures=True)
        for module in registry.values():
            module.shutdown()

    app = FastAPI(title="Crawley", version="0.1.0", lifespan=lifespan)
    app.state.registry = registry
    app.state.executor = executor
    app.include_router(shell_router)
    return app
