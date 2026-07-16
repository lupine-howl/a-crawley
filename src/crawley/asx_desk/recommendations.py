"""ASX recommendation actions and helpers (Sprint 14)."""

from __future__ import annotations

from typing import Any

ACTIONS = ("Buy", "Add", "Hold", "Trim", "Avoid", "Watch")
URGENCIES = ("low", "medium", "high")


def normalize_recommendation(raw: dict[str, Any] | None, *, ticker: str = "") -> dict[str, Any]:
    data = raw if isinstance(raw, dict) else {}
    action = str(data.get("action") or "Watch").strip().title()
    if action not in ACTIONS:
        # common variants
        mapping = {"buy": "Buy", "sell": "Trim", "hold": "Hold", "watch": "Watch", "avoid": "Avoid"}
        action = mapping.get(action.lower(), "Watch")
    urgency = str(data.get("urgency") or "low").lower().strip()
    if urgency not in URGENCIES:
        urgency = "low"
    return {
        "ticker": (str(data.get("ticker") or ticker).strip().upper()),
        "action": action,
        "urgency": urgency,
        "rationale": str(data.get("rationale") or "").strip()[:400],
        "generated_at": str(data.get("generated_at") or ""),
    }
