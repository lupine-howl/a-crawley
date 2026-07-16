"""ASX desk constants and metric helpers (Sprint 13)."""

from __future__ import annotations

import os
from typing import Any

HARD_CEILING = 200
POC_CAP = max(1, min(HARD_CEILING, int(os.environ.get("CRAWLEY_ASX_POC_CAP", "20"))))

SENTIMENTS = ("constructive", "mixed", "cautious", "negative", "unknown")


def normalize_snapshot(raw: dict[str, Any] | None) -> dict[str, Any]:
    data = raw if isinstance(raw, dict) else {}
    sentiment = str(data.get("sentiment") or "unknown").lower().strip()
    if sentiment not in SENTIMENTS:
        sentiment = "unknown"

    def num(key: str) -> float | None:
        val = data.get(key)
        if val is None or val == "":
            return None
        try:
            return float(val)
        except (TypeError, ValueError):
            return None

    return {
        "price": num("price"),
        "change_pct": num("change_pct"),
        "volume": num("volume"),
        "currency": str(data.get("currency") or "AUD"),
        "sentiment": sentiment,
        "headline": str(data.get("headline") or "").strip()[:240],
        "as_of": str(data.get("as_of") or ""),
        "gaps": list(data.get("gaps") or []),
    }


def format_move(change_pct: float | None) -> str:
    if change_pct is None:
        return "—"
    sign = "+" if change_pct >= 0 else ""
    return f"{sign}{change_pct:.2f}%"
