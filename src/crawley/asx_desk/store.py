"""ASX desk persistence under data/investment/asx/."""

from __future__ import annotations

import json
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from crawley.asx_desk.schema import POC_CAP, format_move, normalize_snapshot
from crawley.data.paths import ensure_data_dirs

_lock = threading.RLock()


def asx_dir() -> Path:
    from crawley.data.paths import INVESTMENT_DIR

    ensure_data_dirs()
    path = INVESTMENT_DIR / "asx"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _path(name: str) -> Path:
    return asx_dir() / name


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _write_json(path: Path, data: Any) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def load_universe() -> dict[str, Any]:
    """Load curated universe from package asset (repo) — not runtime-writable."""
    asset = Path(__file__).resolve().parent / "assets" / "universe.json"
    raw = _read_json(asset, {"companies": [], "provenance": {}})
    companies = list(raw.get("companies") or [])
    return {
        "companies": companies,
        "provenance": raw.get("provenance") or {},
        "count": len(companies),
    }


def default_scan_state() -> dict[str, Any]:
    return {
        "status": "idle",
        "cap": POC_CAP,
        "processed": 0,
        "current_ticker": "",
        "current_line": "",
        "last_error": "",
        "company_errors": [],
        "pause_requested": False,
        "updated_at": "",
        "poc_tickers": [],
    }


def load_scan_state() -> dict[str, Any]:
    with _lock:
        state = default_scan_state()
        raw = _read_json(_path("scan_state.json"), {})
        if isinstance(raw, dict):
            state.update(raw)
        state["cap"] = int(state.get("cap") or POC_CAP)
        if not state.get("poc_tickers"):
            universe = load_universe()["companies"]
            state["poc_tickers"] = [c["ticker"] for c in universe[: state["cap"]]]
        return state


def save_scan_state(state: dict[str, Any]) -> None:
    with _lock:
        state = {**state, "updated_at": _now_iso()}
        _write_json(_path("scan_state.json"), state)


def load_scans() -> dict[str, Any]:
    with _lock:
        raw = _read_json(_path("scans.json"), {})
        return dict(raw) if isinstance(raw, dict) else {}


def save_scans(scans: dict[str, Any]) -> None:
    with _lock:
        _write_json(_path("scans.json"), scans)


def load_profiles() -> dict[str, Any]:
    with _lock:
        raw = _read_json(_path("profiles.json"), {})
        return dict(raw) if isinstance(raw, dict) else {}


def save_profiles(profiles: dict[str, Any]) -> None:
    with _lock:
        _write_json(_path("profiles.json"), profiles)


def set_poc_tickers(tickers: list[str]) -> dict[str, Any]:
    universe = {c["ticker"]: c for c in load_universe()["companies"]}
    cleaned = []
    for t in tickers:
        key = (t or "").strip().upper()
        if key in universe and key not in cleaned:
            cleaned.append(key)
    state = load_scan_state()
    state["poc_tickers"] = cleaned[: int(state.get("cap") or POC_CAP)]
    save_scan_state(state)
    return state


def reset_poc_data() -> None:
    with _lock:
        save_scans({})
        save_profiles({})
        state = default_scan_state()
        universe = load_universe()["companies"]
        state["poc_tickers"] = [c["ticker"] for c in universe[:POC_CAP]]
        state["cap"] = POC_CAP
        save_scan_state(state)


def upsert_scan(ticker: str, payload: dict[str, Any]) -> None:
    with _lock:
        scans = load_scans()
        scans[ticker.upper()] = payload
        save_scans(scans)
        state = load_scan_state()
        state["processed"] = sum(
            1 for t in state.get("poc_tickers") or [] if t in scans and scans[t].get("status") == "ready"
        )
        save_scan_state(state)


def desk_rows() -> list[dict[str, Any]]:
    universe = {c["ticker"]: c for c in load_universe()["companies"]}
    state = load_scan_state()
    scans = load_scans()
    rows: list[dict[str, Any]] = []
    for ticker in state.get("poc_tickers") or []:
        meta = universe.get(ticker) or {"ticker": ticker, "name": ticker, "sector": ""}
        scan = scans.get(ticker) or {}
        snap = normalize_snapshot(scan.get("snapshot"))
        status = scan.get("status") or "pending"
        rows.append(
            {
                "ticker": ticker,
                "name": meta.get("name") or ticker,
                "sector": meta.get("sector") or "—",
                "status": status,
                "move": format_move(snap.get("change_pct")),
                "change_pct": snap.get("change_pct"),
                "sentiment": snap.get("sentiment") or "unknown",
                "error": scan.get("error") or "",
                "scanned_at": scan.get("scanned_at") or "",
            }
        )
    return rows


def scan_finished(scan: dict[str, Any] | None) -> bool:
    return (scan or {}).get("status") in {"ready", "error"}


def company_detail(ticker: str) -> dict[str, Any] | None:
    ticker = ticker.upper().strip()
    universe = {c["ticker"]: c for c in load_universe()["companies"]}
    meta = universe.get(ticker)
    if meta is None:
        return None
    scan = load_scans().get(ticker) or {}
    profile = load_profiles().get(ticker) or {
        "markdown": "",
        "status": "empty",
        "error": "",
        "updated_at": "",
    }
    snap = normalize_snapshot(scan.get("snapshot"))
    return {
        "ticker": ticker,
        "name": meta.get("name") or ticker,
        "sector": meta.get("sector") or "—",
        "scan": scan,
        "snapshot": snap,
        "move": format_move(snap.get("change_pct")),
        "profile": profile,
        "sources_used": scan.get("sources_used") or [],
        "headlines": scan.get("headlines") or [],
    }


def progress_view(*, running: bool | None = None) -> dict[str, Any]:
    state = load_scan_state()
    scans = load_scans()
    poc = list(state.get("poc_tickers") or [])
    processed = sum(1 for t in poc if scan_finished(scans.get(t)))
    cap = len(poc) or int(state.get("cap") or POC_CAP)
    remaining = max(0, cap - processed)
    status = state.get("status") or "idle"
    if running is True:
        status = "busy"
    elif running is False and status == "busy":
        status = "paused"
        state["status"] = "paused"
        save_scan_state(state)
    universe = load_universe()
    return {
        **state,
        "status": status,
        "processed": processed,
        "cap": cap,
        "remaining": remaining,
        "universe_count": universe["count"],
        "poc_count": len(poc),
    }


def load_recommendations() -> dict[str, Any]:
    with _lock:
        raw = _read_json(_path("recommendations.json"), {})
        if not isinstance(raw, dict):
            return {"rows": [], "updated_at": "", "status": "idle", "error": ""}
        return {
            "rows": list(raw.get("rows") or []),
            "updated_at": str(raw.get("updated_at") or ""),
            "status": str(raw.get("status") or "idle"),
            "error": str(raw.get("error") or ""),
        }


def save_recommendations(payload: dict[str, Any]) -> None:
    with _lock:
        _write_json(_path("recommendations.json"), payload)
