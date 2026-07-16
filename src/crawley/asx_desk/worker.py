"""Background one-company-at-a-time ASX scanner."""

from __future__ import annotations

import logging
import threading
from datetime import UTC, datetime
from typing import Any

from crawley.asx_desk import fetch as asx_fetch
from crawley.asx_desk import llm_tasks
from crawley.asx_desk.schema import POC_CAP
from crawley.asx_desk.store import (
    load_profiles,
    load_scan_state,
    load_scans,
    load_universe,
    save_profiles,
    save_scan_state,
    scan_finished,
    upsert_scan,
)
from crawley.llm.base import LLMError

logger = logging.getLogger(__name__)

_worker_lock = threading.Lock()
_running = False


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def is_running() -> bool:
    return _running


def request_pause() -> None:
    state = load_scan_state()
    state["pause_requested"] = True
    if state.get("status") == "busy":
        state["current_line"] = "Pause requested…"
    save_scan_state(state)


def start_scan(executor) -> tuple[bool, str]:
    global _running
    with _worker_lock:
        if _running:
            return False, "Scan already running."
        state = load_scan_state()
        poc = list(state.get("poc_tickers") or [])
        if not poc:
            return False, "PoC set is empty — configure tickers first."
        scans = load_scans()
        pending = [t for t in poc if not scan_finished(scans.get(t))]
        if not pending and any(scan_finished(scans.get(t)) for t in poc):
            return False, f"PoC set already scanned ({len(poc)}). Reset to re-run."
        _running = True
        state["status"] = "busy"
        state["pause_requested"] = False
        state["last_error"] = ""
        state["current_line"] = "Starting ASX scan…"
        state["cap"] = len(poc) or POC_CAP
        save_scan_state(state)
    executor.submit(_worker_body)
    return True, "Scan started."


def resume_scan(executor) -> tuple[bool, str]:
    if is_running():
        return False, "Scan already running."
    state = load_scan_state()
    state["pause_requested"] = False
    save_scan_state(state)
    return start_scan(executor)


def regenerate_profile(ticker: str, executor) -> tuple[bool, str]:
    ticker = ticker.upper()
    if ticker not in load_scans():
        return False, "Scan this company first."
    executor.submit(_build_profile, ticker)
    return True, "Updating profile…"


def _company_meta(ticker: str) -> dict[str, Any]:
    for row in load_universe()["companies"]:
        if row["ticker"] == ticker:
            return row
    return {"ticker": ticker, "name": ticker, "sector": ""}


def _build_profile(ticker: str) -> None:
    scan = load_scans().get(ticker) or {}
    company = _company_meta(ticker)
    profiles = load_profiles()
    prior = profiles.get(ticker) or {}
    profiles[ticker] = {
        **prior,
        "status": "generating",
        "error": "",
        "markdown": prior.get("markdown") or "",
        "updated_at": prior.get("updated_at") or "",
    }
    save_profiles(profiles)
    try:
        markdown = llm_tasks.generate_profile(company, scan)
        profiles = load_profiles()
        profiles[ticker] = {
            "markdown": markdown,
            "status": "ready",
            "error": "",
            "updated_at": _now_iso(),
        }
        save_profiles(profiles)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Profile failed for %s", ticker)
        profiles = load_profiles()
        prior = profiles.get(ticker) or {}
        profiles[ticker] = {
            **prior,
            "status": "error",
            "error": str(exc)[:300],
            "updated_at": prior.get("updated_at") or _now_iso(),
        }
        save_profiles(profiles)


def _persist_glance() -> None:
    try:
        from crawley.asx_desk.store import desk_rows, progress_view
        from crawley.data.snapshots import save_snapshot

        progress = progress_view()
        rows = desk_rows()
        lines = [
            "## ASX desk",
            "",
            f"PoC {progress['processed']} / {progress['cap']} scanned · "
            f"universe {progress['universe_count']}",
            "",
        ]
        for row in rows[:8]:
            lines.append(
                f"- **{row['ticker']}** {row['move']} · {row['sentiment']} · {row['status']}"
            )
        save_snapshot("investment", "\n".join(lines))
    except Exception:  # noqa: BLE001
        logger.exception("Failed to persist ASX glance snapshot")


def _worker_body() -> None:
    global _running
    try:
        while True:
            state = load_scan_state()
            if state.get("pause_requested"):
                state["status"] = "paused"
                state["current_line"] = "Paused."
                save_scan_state(state)
                return

            poc = list(state.get("poc_tickers") or [])
            scans = load_scans()
            next_ticker = next(
                (
                    t
                    for t in poc
                    if not scan_finished(scans.get(t))
                ),
                None,
            )
            if not next_ticker:
                state = load_scan_state()
                state["status"] = "done"
                state["pause_requested"] = False
                state["current_line"] = f"PoC scan complete ({len(poc)} / {len(poc)})."
                state["current_ticker"] = ""
                save_scan_state(state)
                _persist_glance()
                return

            company = _company_meta(next_ticker)
            state = load_scan_state()
            state["status"] = "busy"
            state["current_ticker"] = next_ticker
            state["current_line"] = f"Scanning {next_ticker}…"
            save_scan_state(state)

            try:
                result = asx_fetch.scan_company(next_ticker, company.get("name") or next_ticker)
                try:
                    result = llm_tasks.enrich_sentiment(result, company)
                except (LLMError, ValueError) as exc:
                    logger.warning("Sentiment enrich failed for %s: %s", next_ticker, exc)
                    snap = result.get("snapshot") or {}
                    snap["sentiment"] = snap.get("sentiment") or "unknown"
                    result["snapshot"] = snap

                payload = {
                    **result,
                    "status": "ready",
                    "error": "",
                    "scanned_at": result.get("scanned_at") or _now_iso(),
                }
                upsert_scan(next_ticker, payload)
                _build_profile(next_ticker)
                state = load_scan_state()
                ready = sum(
                    1
                    for t in (state.get("poc_tickers") or [])
                    if scan_finished(load_scans().get(t))
                )
                state["current_line"] = (
                    f"Scanned {ready} / {len(state.get('poc_tickers') or [])}: {next_ticker}"
                )
                save_scan_state(state)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Isolated scan failure for %s: %s", next_ticker, exc)
                upsert_scan(
                    next_ticker,
                    {
                        "ticker": next_ticker,
                        "status": "error",
                        "error": str(exc)[:400],
                        "snapshot": {"sentiment": "unknown", "gaps": [str(exc)[:200]]},
                        "headlines": [],
                        "sources_used": [],
                        "scanned_at": _now_iso(),
                    },
                )
                state = load_scan_state()
                errs = list(state.get("company_errors") or [])
                errs.append({"ticker": next_ticker, "error": str(exc)[:300]})
                state["company_errors"] = errs[-30:]
                state["last_error"] = str(exc)[:300]
                state["current_line"] = f"Error on {next_ticker} — continuing"
                save_scan_state(state)
    finally:
        with _worker_lock:
            _running = False
