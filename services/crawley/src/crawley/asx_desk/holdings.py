"""Operator-entered holdings journal (Sprint 27 / B49) — not paper, not broker."""

from __future__ import annotations

import re
import threading
import uuid
from datetime import UTC, datetime
from typing import Any

from crawley.data.paths import ensure_data_dirs

_lock = threading.RLock()

TICKER_RE = re.compile(r"^[A-Z0-9.]{1,12}$")
PROMPT_SLICE_CHARS = 500


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _path():
    from crawley.data.paths import INVESTMENT_DIR

    ensure_data_dirs()
    root = INVESTMENT_DIR / "asx"
    root.mkdir(parents=True, exist_ok=True)
    return root / "holdings_journal.json"


def load_holdings() -> list[dict[str, Any]]:
    with _lock:
        path = _path()
        if not path.exists():
            return []
        try:
            import json

            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return []
        if not isinstance(raw, list):
            return []
        return [normalize_row(r) for r in raw if isinstance(r, dict)]


def save_holdings(rows: list[dict[str, Any]]) -> None:
    import json

    with _lock:
        path = _path()
        cleaned = [normalize_row(r) for r in rows]
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(cleaned, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        tmp.replace(path)


def normalize_row(raw: dict[str, Any] | None) -> dict[str, Any]:
    data = raw if isinstance(raw, dict) else {}
    ticker = str(data.get("ticker") or "").strip().upper()
    try:
        qty = float(data.get("qty") or 0)
    except (TypeError, ValueError):
        qty = 0.0
    return {
        "id": str(data.get("id") or uuid.uuid4()),
        "ticker": ticker,
        "qty": qty,
        "cost_note": str(data.get("cost_note") or "").strip()[:240],
        "note": str(data.get("note") or "").strip()[:240],
        "updated_at": str(data.get("updated_at") or "") or _now_iso(),
    }


def validate_row(*, ticker: str, qty: float) -> str | None:
    ticker = (ticker or "").strip().upper()
    if not ticker or not TICKER_RE.match(ticker):
        return "Ticker must be 1–12 letters/digits (e.g. CBA)."
    if qty <= 0 or qty > 1_000_000_000:
        return "Quantity must be a positive number under 1e9."
    return None


def upsert_holding(
    *,
    holding_id: str = "",
    ticker: str,
    qty: float,
    cost_note: str = "",
    note: str = "",
) -> dict[str, Any]:
    err = validate_row(ticker=ticker, qty=qty)
    if err:
        raise ValueError(err)
    rows = load_holdings()
    row = normalize_row(
        {
            "id": holding_id or str(uuid.uuid4()),
            "ticker": ticker,
            "qty": qty,
            "cost_note": cost_note,
            "note": note,
            "updated_at": _now_iso(),
        }
    )
    out: list[dict[str, Any]] = []
    replaced = False
    for existing in rows:
        if existing.get("id") == row["id"] or (
            not holding_id and existing.get("ticker") == row["ticker"]
        ):
            if not holding_id and existing.get("ticker") == row["ticker"]:
                row["id"] = existing["id"]
            out.append(row)
            replaced = True
        else:
            out.append(existing)
    if not replaced:
        out.append(row)
    save_holdings(out)
    return row


def delete_holding(holding_id: str) -> bool:
    hid = (holding_id or "").strip()
    if not hid:
        return False
    rows = load_holdings()
    kept = [r for r in rows if r.get("id") != hid]
    if len(kept) == len(rows):
        return False
    save_holdings(kept)
    return True


def holdings_prompt_slice(*, max_chars: int = PROMPT_SLICE_CHARS) -> str:
    rows = load_holdings()
    if not rows:
        return ""
    lines = [
        f"- {r['ticker']}: qty={r['qty']}"
        + (f" ({r['cost_note']})" if r.get("cost_note") else "")
        for r in rows[:40]
    ]
    text = (
        "Operator holdings journal (manual; not broker-synced; not paper ledger):\n"
        + "\n".join(lines)
    )
    return text[:max_chars]
