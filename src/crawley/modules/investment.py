"""Investment module — lite bounded search + LLM synthesis."""

from __future__ import annotations

import logging
from concurrent.futures import Executor
from typing import Any

from crawley.jobs import JobState
from crawley.llm.base import ChatMessage, LLMError
from crawley.llm.factory import get_llm_provider
from crawley.modules.contract import Module, ModuleKind, ModuleMeta, ModuleOutput
from crawley.modules.investment_fetch import (
    MAX_ITEMS,
    InvestmentFetchError,
    fetch_rss_items,
    persist_artifacts,
    recent_artifacts,
)

logger = logging.getLogger(__name__)


class InvestmentModule(Module):
    meta = ModuleMeta(
        id="investment",
        title="Investment",
        kind=ModuleKind.LIVE,
        nav_order=10,
        description="Market search and LLM synthesis (lite PoC).",
    )

    def __init__(self) -> None:
        self.job = JobState(
            status="idle",
            message="Ready. Run a small bounded search to synthesize short advice.",
        )
        self._executor: Executor | None = None

    def bind_executor(self, executor: Executor) -> None:
        self._executor = executor

    def panel_context(self) -> dict[str, Any]:
        return {
            "coming_soon": False,
            "description": self.meta.description,
            "job": self.job.to_dict(),
            "recent": recent_artifacts(5),
            "default_query": "US stock market outlook",
            "max_items": MAX_ITEMS,
        }

    def run(self, inputs: dict[str, Any] | None = None) -> ModuleOutput:
        inputs = inputs or {}
        query = (inputs.get("query") or "US stock market outlook").strip()
        if not query:
            return ModuleOutput(error="Query is required.")

        if self.job.status == "busy":
            return ModuleOutput(error="Investment job already running.")

        if self._executor is None:
            return ModuleOutput(error="Executor not configured.")

        self.job = JobState(status="busy", message="Fetching sources…")
        self._executor.submit(self._job_body, query)
        return ModuleOutput(summary="started", details={"status": "busy"})

    def _job_body(self, query: str) -> None:
        try:
            self.job = JobState(status="busy", message="Fetching news headlines…")
            items = fetch_rss_items(query)
            if not items:
                self.job = JobState(
                    status="error",
                    message="No headlines returned. Try a different query.",
                )
                return

            self.job = JobState(
                status="busy",
                message=f"Saving {len(items)} sources and calling LLM…",
            )
            rows = persist_artifacts(query, items)
            prompt = self._build_prompt(query, rows)
            provider = get_llm_provider()
            result = provider.complete(
                [
                    ChatMessage(
                        role="system",
                        content=(
                            "You are a careful personal research assistant. "
                            "Summarize findings into short, actionable notes the user "
                            "can apply manually. Not professional financial advice. "
                            "Keep under 250 words."
                        ),
                    ),
                    ChatMessage(role="user", content=prompt),
                ],
                max_tokens=400,
            )
            self.job = JobState(
                status="done",
                message=f"Done — {len(rows)} sources (query: {query}).",
                summary=result.content,
                details={"query": query, "sources": len(rows), "model": result.model},
            )
        except InvestmentFetchError as exc:
            self.job = JobState(status="error", message=str(exc))
        except LLMError as exc:
            self.job = JobState(status="error", message=str(exc))
        except Exception as exc:  # noqa: BLE001
            logger.exception("Investment job failed")
            self.job = JobState(status="error", message=f"Investment run failed: {exc}")

    @staticmethod
    def _build_prompt(query: str, rows: list[dict[str, str]]) -> str:
        chunks = [f"Query: {query}", "Sources (bounded):"]
        for row in rows:
            chunks.append(f"- {row['title']} ({row['url']}): {row['snippet'][:300]}")
        chunks.append(
            "Write a brief summary and 2–4 practical notes. Manual action only; "
            "no trade orders."
        )
        return "\n".join(chunks)
