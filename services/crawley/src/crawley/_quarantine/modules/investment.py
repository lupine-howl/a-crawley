"""Investment module — bounded search + cache + LLM synthesis."""

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
    InvestmentEmptyError,
    InvestmentFetchError,
    InvestmentNetworkError,
    InvestmentParseError,
    fetch_rss_items,
    persist_artifacts,
    recent_artifacts,
)
from crawley.prompts import build_investment_user_message
from crawley.settings import load_settings

logger = logging.getLogger(__name__)


class InvestmentModule(Module):
    meta = ModuleMeta(
        id="investment",
        title="Investment",
        kind=ModuleKind.LIVE,
        nav_order=10,
        description="ASX research desk — universe scan, company profiles (PoC).",
    )

    def __init__(self) -> None:
        self.job = JobState(
            status="idle",
            message="Ready. Run ASX scan or classic search.",
        )
        self._executor: Executor | None = None

    def bind_executor(self, executor: Executor) -> None:
        self._executor = executor

    def panel_context(self) -> dict[str, Any]:
        from crawley.asx_desk.sources import load_config
        from crawley.asx_desk.store import desk_rows, load_universe, progress_view
        from crawley.asx_desk.worker import is_running

        from crawley.asx_desk.alerts import load_rules, load_triggered, open_alert_count
        from crawley.playbooks import load_playbooks

        progress = progress_view(running=is_running())
        rows = desk_rows()
        universe = load_universe()
        cfg = load_config()
        return {
            "coming_soon": False,
            "description": self.meta.description,
            "job": self.job.to_dict(),
            "recent": recent_artifacts(8),
            "default_query": "ASX market outlook",
            "max_items": MAX_ITEMS,
            "use_cache_default": True,
            "asx_view": "desk",
            "asx_progress": progress,
            "asx_rows": rows,
            "asx_universe_count": universe["count"],
            "asx_provenance": universe.get("provenance") or {},
            "asx_sources": cfg.get("sources") or [],
            "asx_prompts": cfg.get("prompts") or {},
            "poll_asx": progress.get("status") == "busy" or self.job.status == "busy",
            "asx_subnav": "desk",
            "alert_rules": load_rules(),
            "alerts_open": load_triggered(),
            "alert_open_count": open_alert_count(),
            "playbooks": [p for p in load_playbooks() if p.get("desk") == "investment"],
        }

    def company_panel_context(self, ticker: str) -> dict[str, Any] | None:
        from crawley.asx_desk.notebook import has_content, load_notebook
        from crawley.asx_desk.store import company_detail

        detail = company_detail(ticker)
        if detail is None:
            return None
        notebook = load_notebook(ticker)
        ctx = self.panel_context()
        ctx.update(
            {
                "asx_view": "company",
                "company": detail,
                "notebook": notebook,
                "notebook_has_content": has_content(notebook),
                "asx_subnav": "desk",
                "poll_asx": (detail.get("profile") or {}).get("status") == "generating"
                or ctx.get("poll_asx"),
            }
        )
        return ctx

    def recommendations_panel_context(self) -> dict[str, Any]:
        from crawley.asx_desk.feedback import apply_feedback_to_rows
        from crawley.asx_desk.store import load_recommendations

        ctx = self.panel_context()
        recs = load_recommendations()
        rows = apply_feedback_to_rows(list(recs.get("rows") or []))
        recs = {**recs, "rows": rows}
        ctx.update(
            {
                "asx_view": "recommendations",
                "asx_subnav": "recommendations",
                "recommendations": recs,
                "poll_asx": recs.get("status") == "busy" or ctx.get("poll_asx"),
            }
        )
        return ctx

    def portfolio_panel_context(self) -> dict[str, Any]:
        from crawley.asx_desk.portfolio import portfolio_view

        ctx = self.panel_context()
        ctx.update(
            {
                "asx_view": "portfolio",
                "asx_subnav": "portfolio",
                "portfolio": portfolio_view(),
            }
        )
        return ctx

    def holdings_panel_context(self) -> dict[str, Any]:
        from crawley.asx_desk.holdings import load_holdings

        ctx = self.panel_context()
        ctx.update(
            {
                "asx_view": "holdings",
                "asx_subnav": "holdings",
                "holdings": load_holdings(),
            }
        )
        return ctx

    def events_panel_context(self) -> dict[str, Any]:
        from crawley.asx_desk.store import load_events

        ctx = self.panel_context()
        events = load_events()
        ctx.update(
            {
                "asx_view": "events",
                "asx_subnav": "events",
                "events": events,
                "poll_asx": events.get("status") == "busy" or ctx.get("poll_asx"),
            }
        )
        return ctx

    def clusters_panel_context(self) -> dict[str, Any]:
        from crawley.asx_desk.clusters import is_running, load_clusters
        from crawley.markdown_render import render_markdown

        ctx = self.panel_context()
        clusters = load_clusters()
        if is_running():
            clusters = {**clusters, "status": "busy"}
        ctx.update(
            {
                "asx_view": "clusters",
                "asx_subnav": "clusters",
                "clusters": clusters,
                "clusters_html": render_markdown(clusters.get("markdown") or ""),
                "poll_asx": clusters.get("status") == "busy" or ctx.get("poll_asx"),
            }
        )
        return ctx

    def bridge_panel_context(self) -> dict[str, Any]:
        from crawley.bridge.matcher import load_bridge

        ctx = self.panel_context()
        bridge = load_bridge()
        ctx.update(
            {
                "asx_view": "bridge",
                "asx_subnav": "bridge",
                "bridge": bridge,
            }
        )
        return ctx

    def citations_panel_context(self) -> dict[str, Any]:
        from crawley.asx_desk.citations import (
            load_citations,
            load_muted_domains,
            quality_rubric_text,
        )

        ctx = self.panel_context()
        ctx.update(
            {
                "asx_view": "citations",
                "asx_subnav": "citations",
                "citations": load_citations()[-80:],
                "muted_domains": load_muted_domains(),
                "quality_rubric": quality_rubric_text(),
            }
        )
        return ctx

    def run(self, inputs: dict[str, Any] | None = None) -> ModuleOutput:
        inputs = inputs or {}
        query = (inputs.get("query") or "US stock market outlook").strip()
        if not query:
            return ModuleOutput(error="Query is required.")

        use_cache_raw = inputs.get("use_cache", True)
        if isinstance(use_cache_raw, str):
            use_cache = use_cache_raw.lower() in {"1", "true", "on", "yes"}
        else:
            use_cache = bool(use_cache_raw)

        if self.job.status == "busy":
            return ModuleOutput(error="Investment job already running.")

        if self._executor is None:
            return ModuleOutput(error="Executor not configured.")

        self.job = JobState(status="busy", message="Fetching sources…")
        self._executor.submit(self._job_body, query, use_cache)
        return ModuleOutput(summary="started", details={"status": "busy"})

    def _job_body(self, query: str, use_cache: bool = True) -> None:
        try:
            self.job = JobState(status="busy", message="Fetching news headlines…")
            items, fetch_meta = fetch_rss_items(query, use_cache=use_cache)
            cache_note = (
                f" (cache hit from {fetch_meta.get('cached_at', '?')})"
                if fetch_meta.get("cache_hit") == "true"
                else ""
            )

            self.job = JobState(
                status="busy",
                message=f"Saving {len(items)} sources and calling LLM…{cache_note}",
            )
            rows = persist_artifacts(query, items)
            prompt = self._build_prompt(query, rows)
            prompts = load_settings().prompts
            system = prompts.investment_system
            provider = get_llm_provider()
            result = provider.complete(
                [
                    ChatMessage(role="system", content=system),
                    ChatMessage(role="user", content=prompt),
                ],
                max_tokens=450,
            )
            self.job = JobState(
                status="done",
                message=f"Done — {len(rows)} sources (query: {query}){cache_note}.",
                summary=result.content,
                details={
                    "query": query,
                    "sources": len(rows),
                    "model": result.model,
                    "cache_hit": fetch_meta.get("cache_hit"),
                    "cached_at": fetch_meta.get("cached_at"),
                    "prompt_system": system,
                    "prompt_user": prompt,
                    "source_titles": [r["title"] for r in rows],
                },
            )
            try:
                from crawley.data.snapshots import save_snapshot

                save_snapshot("investment", result.content)
            except Exception:  # noqa: BLE001
                logger.exception("Failed to persist investment snapshot")
        except InvestmentEmptyError as exc:
            self.job = JobState(status="error", message=f"Empty results: {exc}")
        except InvestmentNetworkError as exc:
            self.job = JobState(status="error", message=f"Network: {exc}")
        except InvestmentParseError as exc:
            self.job = JobState(status="error", message=f"Parse: {exc}")
        except InvestmentFetchError as exc:
            self.job = JobState(status="error", message=str(exc))
        except LLMError as exc:
            self.job = JobState(status="error", message=f"LLM: {exc}")
        except Exception as exc:  # noqa: BLE001
            logger.exception("Investment job failed")
            self.job = JobState(status="error", message=f"Investment run failed: {exc}")

    @staticmethod
    def _build_prompt(query: str, rows: list[dict[str, str]]) -> str:
        prompts = load_settings().prompts
        lines = []
        for row in rows:
            meta = []
            if row.get("publisher"):
                meta.append(row["publisher"])
            if row.get("published"):
                meta.append(row["published"])
            meta_s = f" [{'; '.join(meta)}]" if meta else ""
            lines.append(
                f"- {row['title']}{meta_s} ({row['url']}): {row['snippet'][:300]}"
            )
        return build_investment_user_message(
            query=query,
            source_lines=lines,
            footer=prompts.investment_user_footer,
        )
