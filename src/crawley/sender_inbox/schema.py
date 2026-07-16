"""Sender Inbox categorization schema (Sprint 12)."""

from __future__ import annotations

import hashlib
import os
import re
from typing import Any

# Hard ceiling 200. Operator cap lives in Settings (scale.inbox_cap); env sets default.
HARD_CEILING = 200
POC_CAP = max(1, min(HARD_CEILING, int(os.environ.get("CRAWLEY_SENDER_INBOX_CAP", "20"))))

URGENCY_LEVELS = ("low", "medium", "high", "critical")
CATEGORIES = ("personal", "work", "billing", "newsletter", "other")

# Quiet signals omitted from UI chips.
SIGNAL_PRIORITY = (
    "urgent",
    "reply",
    "action",
    "vip",
    "billing",
    "newsletter",
)


def sender_id_for(from_addr: str) -> str:
    addr = (from_addr or "").strip().lower()
    if not addr:
        addr = "unknown"
    return hashlib.sha256(addr.encode("utf-8")).hexdigest()[:16]


def normalize_metrics(raw: dict[str, Any] | None) -> dict[str, Any]:
    """Coerce LLM / stored metrics onto the documented schema."""
    data = raw if isinstance(raw, dict) else {}
    urgency = str(data.get("urgency") or "low").lower().strip()
    if urgency not in URGENCY_LEVELS:
        urgency = "low"
    category = str(data.get("category") or "other").lower().strip()
    if category not in CATEGORIES:
        category = "other"
    requires_reply = bool(data.get("requires_reply"))
    action_needed = bool(data.get("action_needed"))
    vip = bool(data.get("vip"))
    brief = str(data.get("brief") or "").strip()[:240]

    signals: list[str] = []
    for item in data.get("signals") or []:
        token = re.sub(r"[^a-z0-9_-]+", "", str(item).lower().strip())
        if token and token not in signals:
            signals.append(token)
    if urgency in {"high", "critical"} and "urgent" not in signals:
        signals.insert(0, "urgent")
    if requires_reply and "reply" not in signals:
        signals.append("reply")
    if action_needed and "action" not in signals:
        signals.append("action")
    if vip and "vip" not in signals:
        signals.append("vip")
    if category in {"billing", "newsletter"} and category not in signals:
        signals.append(category)

    # Cap and order for chips.
    ordered = [s for s in SIGNAL_PRIORITY if s in signals]
    ordered.extend(s for s in signals if s not in ordered)
    signals = ordered[:5]

    return {
        "urgency": urgency,
        "requires_reply": requires_reply,
        "action_needed": action_needed,
        "vip": vip,
        "category": category,
        "signals": signals,
        "brief": brief,
    }


def signal_chips(metrics: dict[str, Any] | None, *, limit: int = 3) -> list[str]:
    """UI chip labels — skip quiet-only categories."""
    m = normalize_metrics(metrics)
    chips: list[str] = []
    for sig in m["signals"]:
        if sig in {"newsletter"} and not m["requires_reply"] and m["urgency"] == "low":
            continue
        chips.append(sig)
        if len(chips) >= limit:
            break
    return chips


def sort_weight(metrics: dict[str, Any] | None) -> int:
    m = normalize_metrics(metrics)
    weight = 0
    if m["urgency"] == "critical":
        weight += 40
    elif m["urgency"] == "high":
        weight += 25
    elif m["urgency"] == "medium":
        weight += 10
    if m["requires_reply"]:
        weight += 15
    if m["vip"]:
        weight += 8
    return weight
