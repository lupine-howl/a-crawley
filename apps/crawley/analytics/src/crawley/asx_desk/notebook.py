"""ASX research notebook / thesis notes (Sprint 23 / B45)."""

from __future__ import annotations

import json
import threading
from datetime import UTC, datetime
from typing import Any

from crawley.data.paths import ensure_data_dirs

_lock = threading.RLock()

MAX_NOTEBOOK_CHARS = 4000
PROMPT_SLICE_CHARS = 600


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _root():
    from crawley.data.paths import INVESTMENT_DIR

    ensure_data_dirs()
    path = INVESTMENT_DIR / "asx" / "notebooks"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _path(ticker: str):
    ticker = (ticker or "").strip().upper()
    return _root() / f"{ticker}.json"


def empty_notebook(ticker: str) -> dict[str, Any]:
    return {
        "ticker": (ticker or "").strip().upper(),
        "thesis": "",
        "notes": "",
        "updated_at": "",
    }


def load_notebook(ticker: str) -> dict[str, Any]:
    ticker = (ticker or "").strip().upper()
    if not ticker:
        return empty_notebook("")
    with _lock:
        path = _path(ticker)
        if not path.exists():
            return empty_notebook(ticker)
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return empty_notebook(ticker)
        if not isinstance(raw, dict):
            return empty_notebook(ticker)
        return {
            "ticker": ticker,
            "thesis": str(raw.get("thesis") or "")[:MAX_NOTEBOOK_CHARS],
            "notes": str(raw.get("notes") or "")[:MAX_NOTEBOOK_CHARS],
            "updated_at": str(raw.get("updated_at") or ""),
        }


def save_notebook(ticker: str, *, thesis: str = "", notes: str = "") -> dict[str, Any]:
    ticker = (ticker or "").strip().upper()
    if not ticker:
        raise ValueError("Ticker required")
    row = {
        "ticker": ticker,
        "thesis": (thesis or "").strip()[:MAX_NOTEBOOK_CHARS],
        "notes": (notes or "").strip()[:MAX_NOTEBOOK_CHARS],
        "updated_at": _now_iso(),
    }
    with _lock:
        path = _path(ticker)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(row, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        tmp.replace(path)
    return row


def notebook_prompt_slice(ticker: str = "", *, max_chars: int = PROMPT_SLICE_CHARS) -> str:
    """Hard-capped thesis/notes for profile/recommend prompts. Empty → ''."""
    if ticker:
        nb = load_notebook(ticker)
        parts = []
        if nb.get("thesis"):
            parts.append(f"Thesis: {nb['thesis']}")
        if nb.get("notes"):
            parts.append(f"Notes: {nb['notes']}")
        if not parts:
            return ""
        text = f"Operator notebook for {nb['ticker']}:\n" + "\n".join(parts)
        return text[:max_chars]

    # Multi-ticker slice for recommendations: active notebooks only.
    lines: list[str] = []
    root = _root()
    for path in sorted(root.glob("*.json"))[:30]:
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(raw, dict):
            continue
        t = str(raw.get("ticker") or path.stem).upper()
        thesis = str(raw.get("thesis") or "").strip()
        notes = str(raw.get("notes") or "").strip()
        if not thesis and not notes:
            continue
        snippet = thesis or notes
        lines.append(f"- {t}: {snippet[:120]}")
    if not lines:
        return ""
    text = "Operator notebooks (respect; non-order advice only):\n" + "\n".join(lines)
    return text[:max_chars]


def has_content(notebook: dict[str, Any] | None) -> bool:
    if not notebook:
        return False
    return bool((notebook.get("thesis") or "").strip() or (notebook.get("notes") or "").strip())
