"""Holdings-aware mail ↔ ASX ticker matching.

Approach (documented for architecture):
- Allowlist = active ASX set ∪ paper portfolio tickers (not full mailbox × universe).
- Match whole-word ticker tokens (``\\bTICKER\\b``) in subject / snippet / body / from.
- Optional company-name match when name length ≥ 5 (reduces short-token noise).
- Min ticker length 2 (ASX codes); English stop-ish tokens excluded.
- No auto-trading; no auto-send — digest + deep links only.
"""

from __future__ import annotations

import json
import re
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from crawley.data.paths import ensure_data_dirs

_lock = threading.RLock()

# Tokens that collide with English / common noise even as ASX codes.
BLOCKLIST = frozenset(
    {
        "AN",
        "OR",
        "IT",
        "AT",
        "BE",
        "DO",
        "GO",
        "IF",
        "IN",
        "IS",
        "ME",
        "MY",
        "NO",
        "ON",
        "SO",
        "TO",
        "UP",
        "US",
        "WE",
        "ALL",
        "AND",
        "ANY",
        "ARE",
        "FOR",
        "THE",
        "NEW",
        "ONE",
        "TWO",
        "OUT",
        "NOW",
        "DAY",
        "AGE",
    }
)

MIN_TICKER_LEN = 2
MAX_HITS = 60
MAX_MESSAGES_SCANNED = 200


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def bridge_path() -> Path:
    from crawley.data.paths import INVESTMENT_DIR

    ensure_data_dirs()
    path = INVESTMENT_DIR / "asx"
    path.mkdir(parents=True, exist_ok=True)
    return path / "bridge.json"


def load_bridge() -> dict[str, Any]:
    path = bridge_path()
    if not path.exists():
        return {"status": "idle", "hits": [], "markdown": "", "updated_at": "", "error": ""}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"status": "idle", "hits": [], "markdown": "", "updated_at": "", "error": ""}
    if not isinstance(raw, dict):
        return {"status": "idle", "hits": [], "markdown": "", "updated_at": "", "error": ""}
    return {
        "status": raw.get("status") or "idle",
        "hits": list(raw.get("hits") or []),
        "markdown": raw.get("markdown") or "",
        "updated_at": raw.get("updated_at") or "",
        "error": raw.get("error") or "",
        "stats": raw.get("stats") or {},
    }


def save_bridge(payload: dict[str, Any]) -> None:
    with _lock:
        path = bridge_path()
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        tmp.replace(path)


def build_allowlist() -> dict[str, dict[str, Any]]:
    """ticker → {name, in_poc, in_portfolio}."""
    from crawley.asx_desk.portfolio import load_portfolio
    from crawley.asx_desk.store import load_scan_state, load_universe

    universe = {c["ticker"]: c for c in load_universe()["companies"]}
    poc = set(load_scan_state().get("poc_tickers") or [])
    portfolio = load_portfolio()
    holdings = set((portfolio.get("positions") or {}).keys())
    tickers = poc | holdings
    out: dict[str, dict[str, Any]] = {}
    for t in sorted(tickers):
        meta = universe.get(t) or {"ticker": t, "name": t}
        name = str(meta.get("name") or t)
        if len(t) < MIN_TICKER_LEN:
            continue
        if t in BLOCKLIST:
            continue
        out[t] = {
            "ticker": t,
            "name": name,
            "in_poc": t in poc,
            "in_portfolio": t in holdings,
        }
    return out


def _haystack(msg: dict[str, Any]) -> str:
    parts = [
        msg.get("subject") or "",
        msg.get("snippet") or "",
        msg.get("body_text") or "",
        msg.get("from_name") or "",
        msg.get("from_addr") or "",
    ]
    metrics = msg.get("metrics") or {}
    if isinstance(metrics, dict):
        parts.append(str(metrics.get("brief") or ""))
    return "\n".join(parts)


def match_message(msg: dict[str, Any], allowlist: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    text = _haystack(msg)
    if not text.strip():
        return []
    hits: list[dict[str, Any]] = []
    seen: set[str] = set()
    for ticker, meta in allowlist.items():
        if ticker in seen:
            continue
        pattern = re.compile(rf"\b{re.escape(ticker)}\b", re.IGNORECASE)
        matched_via = ""
        if pattern.search(text):
            matched_via = "ticker"
        else:
            name = meta.get("name") or ""
            if len(name) >= 5 and re.search(re.escape(name), text, re.IGNORECASE):
                matched_via = "name"
        if not matched_via:
            continue
        seen.add(ticker)
        hits.append(
            {
                "ticker": ticker,
                "company_name": meta.get("name") or ticker,
                "matched_via": matched_via,
                "in_poc": meta.get("in_poc"),
                "in_portfolio": meta.get("in_portfolio"),
                "message_id": msg.get("id") or "",
                "sender_id": msg.get("sender_id") or "",
                "from_addr": msg.get("from_addr") or "",
                "from_name": msg.get("from_name") or "",
                "subject": (msg.get("subject") or "")[:200],
                "snippet": (msg.get("snippet") or "")[:240],
                "internal_date": msg.get("internal_date") or "",
            }
        )
    return hits


def run_bridge_scan() -> dict[str, Any]:
    from crawley.sender_inbox.store import load_messages

    allowlist = build_allowlist()
    messages = load_messages()
    messages = sorted(
        messages,
        key=lambda m: m.get("internal_date") or "",
        reverse=True,
    )[:MAX_MESSAGES_SCANNED]
    hits: list[dict[str, Any]] = []
    for msg in messages:
        for hit in match_message(msg, allowlist):
            hits.append(hit)
            if len(hits) >= MAX_HITS:
                break
        if len(hits) >= MAX_HITS:
            break

    md = [
        "# Email × ASX bridge",
        "",
        "Mentions of active-set / paper tickers in Sender Inbox. "
        "Not advice · no auto-trading · no auto-send.",
        "",
        f"Allowlist: {len(allowlist)} tickers · messages scanned: {len(messages)} · hits: {len(hits)}",
        "",
    ]
    if not hits:
        md.append("_No matches in the bounded ingest set._")
    else:
        md.append("| Ticker | Sender | Subject | Via |")
        md.append("| --- | --- | --- | --- |")
        for h in hits:
            subj = (h.get("subject") or "").replace("|", "/")
            who = (h.get("from_name") or h.get("from_addr") or "—").replace("|", "/")
            md.append(
                f"| [{h['ticker']}](/modules/investment/companies/{h['ticker']}) "
                f"| [{who}](/modules/gmail/senders/{h['sender_id']}) "
                f"| {subj} | {h.get('matched_via')} |"
            )

    payload = {
        "status": "ready",
        "hits": hits,
        "markdown": "\n".join(md),
        "updated_at": _now_iso(),
        "error": "",
        "stats": {
            "allowlist": len(allowlist),
            "messages_scanned": len(messages),
            "hits": len(hits),
        },
    }
    save_bridge(payload)
    return payload
