"""Recommendation disposition feedback (Sprint 19)."""

from __future__ import annotations

import json
import threading
from datetime import UTC, datetime, timedelta
from typing import Any

from crawley.data.paths import ensure_data_dirs

_lock = threading.RLock()

DISPOSITIONS = ("accepted", "dismissed", "snoozed")


def _now() -> datetime:
    return datetime.now(UTC)


def _now_iso() -> str:
    return _now().replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _path():
    from crawley.data.paths import INVESTMENT_DIR

    ensure_data_dirs()
    root = INVESTMENT_DIR / "asx"
    root.mkdir(parents=True, exist_ok=True)
    return root / "recommendation_feedback.json"


def load_feedback() -> dict[str, Any]:
    """ticker → {disposition, note, at, until}."""
    with _lock:
        path = _path()
        if not path.exists():
            return {}
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        return dict(raw) if isinstance(raw, dict) else {}


def save_feedback(data: dict[str, Any]) -> None:
    with _lock:
        path = _path()
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        tmp.replace(path)


def set_disposition(
    ticker: str,
    disposition: str,
    *,
    note: str = "",
    snooze_hours: int = 72,
) -> dict[str, Any]:
    ticker = (ticker or "").strip().upper()
    disposition = (disposition or "").strip().lower()
    if not ticker:
        raise ValueError("Ticker required.")
    if disposition not in DISPOSITIONS:
        raise ValueError("Disposition must be accepted, dismissed, or snoozed.")
    data = load_feedback()
    until = ""
    if disposition == "snoozed":
        until = (
            (_now() + timedelta(hours=max(1, snooze_hours)))
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z")
        )
    row = {
        "ticker": ticker,
        "disposition": disposition,
        "note": (note or "").strip()[:240],
        "at": _now_iso(),
        "until": until,
    }
    data[ticker] = row
    save_feedback(data)
    return row


def clear_disposition(ticker: str) -> None:
    data = load_feedback()
    data.pop((ticker or "").strip().upper(), None)
    save_feedback(data)


def active_feedback() -> dict[str, dict[str, Any]]:
    """Feedback still in effect (dismissed always; snoozed until expiry)."""
    now = _now_iso()
    out: dict[str, dict[str, Any]] = {}
    for ticker, row in load_feedback().items():
        disp = row.get("disposition")
        if disp == "dismissed":
            out[ticker] = row
        elif disp == "snoozed" and (row.get("until") or "") > now:
            out[ticker] = row
        elif disp == "accepted":
            out[ticker] = row
    return out


def apply_feedback_to_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Annotate rows; hide dismissed; mark snoozed/accepted."""
    fb = active_feedback()
    out: list[dict[str, Any]] = []
    for row in rows:
        ticker = row.get("ticker") or ""
        meta = fb.get(ticker)
        annotated = {**row}
        if meta:
            disp = meta.get("disposition")
            annotated["feedback"] = disp
            annotated["feedback_note"] = meta.get("note") or ""
            if disp == "dismissed":
                annotated["hidden"] = True
            elif disp == "snoozed":
                annotated["snoozed"] = True
            elif disp == "accepted":
                annotated["accepted"] = True
        else:
            annotated["feedback"] = ""
        if annotated.get("hidden"):
            continue
        out.append(annotated)
    return out


def feedback_prompt_slice(*, max_chars: int = 400) -> str:
    """Capped note for regenerate prompts."""
    lines = []
    for ticker, row in sorted(active_feedback().items()):
        disp = row.get("disposition")
        note = row.get("note") or ""
        lines.append(f"- {ticker}: {disp}" + (f" ({note})" if note else ""))
    text = "Operator feedback (respect; do not re-push dismissed):\n" + "\n".join(lines)
    return text[:max_chars] if lines else ""
