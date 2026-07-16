"""Local ASX desk alerts — informational only (Sprint 19)."""

from __future__ import annotations

import json
import threading
import uuid
from datetime import UTC, datetime
from typing import Any

from crawley.data.paths import ensure_data_dirs

_lock = threading.RLock()

CONDITIONS = ("keyword", "move_pct")


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _path(name: str):
    from crawley.data.paths import INVESTMENT_DIR

    ensure_data_dirs()
    root = INVESTMENT_DIR / "asx"
    root.mkdir(parents=True, exist_ok=True)
    return root / name


def _read(name: str, default: Any) -> Any:
    path = _path(name)
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _write(name: str, data: Any) -> None:
    path = _path(name)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def load_rules() -> list[dict[str, Any]]:
    with _lock:
        raw = _read("alert_rules.json", [])
        return list(raw) if isinstance(raw, list) else []


def save_rules(rules: list[dict[str, Any]]) -> None:
    with _lock:
        _write("alert_rules.json", rules)


def load_triggered() -> list[dict[str, Any]]:
    with _lock:
        raw = _read("alerts_triggered.json", [])
        rows = list(raw) if isinstance(raw, list) else []
        # Drop dismissed/snoozed that expired
        now = _now_iso()
        keep = []
        for r in rows:
            if r.get("status") == "snoozed" and (r.get("snooze_until") or "") > now:
                keep.append(r)
            elif r.get("status") in {"open", "snoozed"}:
                if r.get("status") == "snoozed" and (r.get("snooze_until") or "") <= now:
                    r = {**r, "status": "open", "snooze_until": ""}
                if r.get("status") == "open":
                    keep.append(r)
            # dismissed dropped
        return keep


def save_triggered(rows: list[dict[str, Any]]) -> None:
    with _lock:
        _write("alerts_triggered.json", rows[-100:])


def add_rule(
    *,
    ticker: str = "",
    condition: str = "keyword",
    value: str = "",
    note: str = "",
) -> dict[str, Any]:
    ticker = (ticker or "").strip().upper()
    condition = (condition or "keyword").strip().lower()
    if condition not in CONDITIONS:
        condition = "keyword"
    value = (value or "").strip()[:120]
    if not value:
        raise ValueError("Alert value is required (keyword or move %).")
    rule = {
        "id": uuid.uuid4().hex[:12],
        "ticker": ticker,  # empty = any active-set ticker
        "condition": condition,
        "value": value,
        "note": (note or "").strip()[:200],
        "created_at": _now_iso(),
        "enabled": True,
    }
    rules = load_rules()
    rules.append(rule)
    save_rules(rules)
    return rule


def delete_rule(rule_id: str) -> bool:
    rules = load_rules()
    kept = [r for r in rules if r.get("id") != rule_id]
    if len(kept) == len(rules):
        return False
    save_rules(kept)
    return True


def dismiss_alert(alert_id: str) -> None:
    rows = load_triggered()
    save_triggered([r for r in rows if r.get("id") != alert_id])


def snooze_alert(alert_id: str, *, hours: int = 24) -> None:
    from datetime import timedelta

    until = (
        datetime.now(UTC) + timedelta(hours=max(1, hours))
    ).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    rows = load_triggered()
    for r in rows:
        if r.get("id") == alert_id:
            r["status"] = "snoozed"
            r["snooze_until"] = until
    save_triggered(rows)


def evaluate_alerts() -> list[dict[str, Any]]:
    """Evaluate rules against latest scans — informational only; no trades."""
    from crawley.asx_desk.schema import normalize_snapshot
    from crawley.asx_desk.store import load_scan_state, load_scans

    rules = [r for r in load_rules() if r.get("enabled", True)]
    if not rules:
        return load_triggered()

    state = load_scan_state()
    poc = set(state.get("poc_tickers") or [])
    scans = load_scans()
    existing = {(a.get("rule_id"), a.get("ticker"), a.get("message")): a for a in load_triggered()}
    new_rows = list(load_triggered())

    for rule in rules:
        tickers = [rule["ticker"]] if rule.get("ticker") else sorted(poc)
        for ticker in tickers:
            if ticker and ticker not in poc and rule.get("ticker"):
                # Rule targets ticker outside active set — still check if scanned
                pass
            scan = scans.get(ticker) or {}
            snap = normalize_snapshot(scan.get("snapshot"))
            headlines = scan.get("headlines") or []
            hit_msg = ""
            if rule["condition"] == "keyword":
                needle = rule["value"].lower()
                hay = " ".join(
                    [snap.get("headline") or ""]
                    + [h.get("title") or "" for h in headlines if isinstance(h, dict)]
                ).lower()
                if needle and needle in hay:
                    hit_msg = f"Keyword “{rule['value']}” matched on {ticker}"
            elif rule["condition"] == "move_pct":
                try:
                    threshold = abs(float(rule["value"]))
                except ValueError:
                    continue
                move = snap.get("change_pct")
                if move is not None and abs(float(move)) >= threshold:
                    hit_msg = f"{ticker} move {move:+.2f}% ≥ ±{threshold:g}%"
            if not hit_msg:
                continue
            key = (rule["id"], ticker, hit_msg)
            if key in existing:
                continue
            alert = {
                "id": uuid.uuid4().hex[:12],
                "rule_id": rule["id"],
                "ticker": ticker,
                "message": hit_msg,
                "note": rule.get("note") or "",
                "status": "open",
                "snooze_until": "",
                "triggered_at": _now_iso(),
            }
            new_rows.append(alert)
            existing[key] = alert

    save_triggered(new_rows[-100:])
    return load_triggered()


def open_alert_count() -> int:
    return sum(1 for a in load_triggered() if a.get("status") == "open")
