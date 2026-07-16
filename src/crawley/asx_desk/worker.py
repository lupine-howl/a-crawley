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


def _expand_active_set_for_local_llm() -> None:
    """Local Llama has no per-call cost — prefer the hard ceiling / full universe pad."""
    from crawley.asx_desk.store import sync_active_cap
    from crawley.settings import HARD_SCALE_CEILING, resolved_llm_provider_name

    name = resolved_llm_provider_name()
    if name not in {"local_llama", "local", "llama"}:
        return
    sync_active_cap(HARD_SCALE_CEILING, expand_from_universe=True)


def _clear_scan_progress_for_active_set() -> None:
    """Drop scan/profile rows for the active set so a re-run can proceed."""
    from crawley.asx_desk.store import load_profiles, load_scans, save_profiles, save_scans

    state = load_scan_state()
    poc = set(state.get("poc_tickers") or [])
    if not poc:
        return
    scans = {k: v for k, v in load_scans().items() if k not in poc}
    profiles = {k: v for k, v in load_profiles().items() if k not in poc}
    save_scans(scans)
    save_profiles(profiles)
    state["processed"] = 0
    state["status"] = "idle"
    state["current_line"] = ""
    state["last_error"] = ""
    save_scan_state(state)


def start_scan(executor, *, force: bool = False) -> tuple[bool, str]:
    global _running
    _expand_active_set_for_local_llm()
    with _worker_lock:
        if _running:
            return False, "Scan already running."
        state = load_scan_state()
        poc = list(state.get("poc_tickers") or [])
        if not poc:
            return False, "Active set is empty — configure tickers first."
        scans = load_scans()
        pending = [t for t in poc if not scan_finished(scans.get(t))]
        if not pending and any(scan_finished(scans.get(t)) for t in poc):
            if not force:
                return False, f"Active set already scanned ({len(poc)}). Reset or start with force."
            _clear_scan_progress_for_active_set()
            state = load_scan_state()
            poc = list(state.get("poc_tickers") or [])
        _running = True
        state["status"] = "busy"
        state["pause_requested"] = False
        state["last_error"] = ""
        state["current_line"] = "Starting ASX scan…"
        state["cap"] = len(poc) or POC_CAP
        save_scan_state(state)
    executor.submit(_worker_body)
    return True, "Scan started."


def stop_scan() -> tuple[bool, str]:
    """Request pause / stop of the running scan loop."""
    if not is_running():
        state = load_scan_state()
        if state.get("status") == "busy":
            request_pause()
            return True, "Stop requested."
        return False, "Scan is not running."
    request_pause()
    return True, "Stop requested."


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


def refresh_recommendations(executor) -> tuple[bool, str]:
    from crawley.asx_desk.store import load_recommendations, save_recommendations

    state = load_scan_state()
    poc = list(state.get("poc_tickers") or [])
    profiles = load_profiles()
    if not any(profiles.get(t, {}).get("markdown") for t in poc):
        return False, "Scan and profile at least one PoC company first."
    payload = load_recommendations()
    payload["status"] = "busy"
    payload["error"] = ""
    save_recommendations(payload)
    executor.submit(_recommendations_body)
    return True, "Refreshing recommendations…"


def _recommendations_body() -> None:
    from crawley.asx_desk import llm_tasks
    from crawley.asx_desk.store import (
        desk_rows,
        load_profiles,
        load_recommendations,
        save_recommendations,
    )

    try:
        rows_in = []
        profiles = load_profiles()
        for row in desk_rows():
            if row["status"] not in {"ready", "error"}:
                continue
            prof = profiles.get(row["ticker"]) or {}
            rows_in.append(
                {
                    "ticker": row["ticker"],
                    "name": row["name"],
                    "sector": row["sector"],
                    "move": row["move"],
                    "sentiment": row["sentiment"],
                    "profile_excerpt": (prof.get("markdown") or "")[:240],
                }
            )
        generated = llm_tasks.generate_recommendations(rows_in)
        save_recommendations(
            {
                "rows": generated,
                "updated_at": _now_iso(),
                "status": "ready",
                "error": "",
            }
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Recommendations refresh failed")
        payload = load_recommendations()
        payload["status"] = "error"
        payload["error"] = str(exc)[:300]
        save_recommendations(payload)


# Hard cap on event rows per refresh (active set × headlines/ticker still polite).
EVENTS_MAX_ROWS = 80
EVENTS_PER_TICKER = 2


def refresh_events(executor) -> tuple[bool, str]:
    from crawley.asx_desk.store import load_events, load_scan_state, save_events

    state = load_scan_state()
    poc = list(state.get("poc_tickers") or [])
    if not poc:
        return False, "Active set is empty — configure tickers first."
    payload = load_events()
    payload["status"] = "busy"
    payload["error"] = ""
    save_events(payload)
    executor.submit(_events_body)
    return True, "Refreshing earnings/events skim…"


def _events_body() -> None:
    from crawley.asx_desk.store import (
        load_events,
        load_scan_state,
        load_universe,
        save_events,
    )

    try:
        state = load_scan_state()
        poc = list(state.get("poc_tickers") or [])
        universe = {c["ticker"]: c for c in load_universe()["companies"]}
        events: list[dict[str, Any]] = []
        for ticker in poc:
            if len(events) >= EVENTS_MAX_ROWS:
                break
            meta = universe.get(ticker) or {"name": ticker}
            rows = asx_fetch.fetch_events_for_ticker(
                ticker, meta.get("name") or ticker, limit=EVENTS_PER_TICKER
            )
            events.extend(rows)
            asx_fetch.time.sleep(asx_fetch.RATE_LIMIT_S)
        md_lines = [
            "# ASX earnings & events skim",
            "",
            f"Active set: {len(poc)} · rows: {len(events)} · not licensed research.",
            "",
        ]
        if not events:
            md_lines.append("_No event-like headlines found for the active set._")
        else:
            md_lines.append("| Ticker | Headline | When |")
            md_lines.append("| --- | --- | --- |")
            for ev in events[:EVENTS_MAX_ROWS]:
                title = (ev.get("title") or "").replace("|", "/")
                md_lines.append(
                    f"| {ev.get('ticker')} | {title} | {(ev.get('published') or '—')[:24]} |"
                )
        save_events(
            {
                "status": "ready",
                "events": events[:EVENTS_MAX_ROWS],
                "markdown": "\n".join(md_lines),
                "updated_at": _now_iso(),
                "error": "",
            }
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Events skim failed")
        payload = load_events()
        payload["status"] = "error"
        payload["error"] = str(exc)[:300]
        save_events(payload)


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
                try:
                    from crawley.asx_desk.alerts import evaluate_alerts

                    evaluate_alerts()
                except Exception:  # noqa: BLE001
                    logger.exception("Alert evaluation failed")
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
