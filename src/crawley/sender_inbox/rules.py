"""Local VIP / muted sender rules (Sprint 24 / B46)."""

from __future__ import annotations

import json
import re
import threading
from datetime import UTC, datetime
from typing import Any

from crawley.data.paths import ensure_data_dirs
from crawley.sender_inbox.schema import sender_id_for
from crawley.sender_inbox.store import inbox_dir

_lock = threading.RLock()

PRIORITIES = ("vip", "muted", "normal")


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def rules_path():
    ensure_data_dirs()
    return inbox_dir() / "sender_rules.json"


def load_rules() -> list[dict[str, Any]]:
    with _lock:
        path = rules_path()
        if not path.exists():
            return []
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        if isinstance(raw, list):
            return [normalize_rule(r) for r in raw if isinstance(r, dict)]
        if isinstance(raw, dict):
            # Allow map keyed by sender_id
            return [normalize_rule({**v, "sender_id": k}) for k, v in raw.items() if isinstance(v, dict)]
        return []


def save_rules(rules: list[dict[str, Any]]) -> None:
    with _lock:
        path = rules_path()
        cleaned = [normalize_rule(r) for r in rules]
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(cleaned, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        tmp.replace(path)


def normalize_rule(raw: dict[str, Any] | None) -> dict[str, Any]:
    data = raw if isinstance(raw, dict) else {}
    addr = str(data.get("from_addr") or "").strip().lower()
    sid = str(data.get("sender_id") or "").strip() or (sender_id_for(addr) if addr else "")
    priority = str(data.get("priority") or "normal").lower().strip()
    if priority not in PRIORITIES:
        priority = "normal"
    tags: list[str] = []
    for item in data.get("tags") or []:
        token = re.sub(r"[^a-z0-9_-]+", "", str(item).lower().strip())
        if token and token not in tags:
            tags.append(token)
    return {
        "sender_id": sid,
        "from_addr": addr,
        "priority": priority,
        "tags": tags[:8],
        "note": str(data.get("note") or "").strip()[:240],
        "updated_at": str(data.get("updated_at") or "") or _now_iso(),
    }


def get_rule(sender_id: str = "", *, from_addr: str = "") -> dict[str, Any] | None:
    sid = (sender_id or "").strip() or sender_id_for(from_addr)
    addr = (from_addr or "").strip().lower()
    for rule in load_rules():
        if sid and rule.get("sender_id") == sid:
            return rule
        if addr and rule.get("from_addr") == addr:
            return rule
    return None


def upsert_rule(
    *,
    sender_id: str = "",
    from_addr: str = "",
    priority: str = "normal",
    tags: list[str] | None = None,
    note: str = "",
) -> dict[str, Any]:
    addr = (from_addr or "").strip().lower()
    sid = (sender_id or "").strip() or sender_id_for(addr)
    if not sid and not addr:
        raise ValueError("sender_id or from_addr required")
    rules = load_rules()
    rule = normalize_rule(
        {
            "sender_id": sid,
            "from_addr": addr,
            "priority": priority,
            "tags": tags or [],
            "note": note,
            "updated_at": _now_iso(),
        }
    )
    out: list[dict[str, Any]] = []
    replaced = False
    for existing in rules:
        if existing.get("sender_id") == rule["sender_id"] or (
            rule["from_addr"] and existing.get("from_addr") == rule["from_addr"]
        ):
            # Preserve address if update omitted it
            if not rule["from_addr"]:
                rule["from_addr"] = existing.get("from_addr") or ""
            out.append(rule)
            replaced = True
        else:
            out.append(existing)
    if not replaced:
        out.append(rule)
    save_rules(out)
    return rule


def delete_rule(sender_id: str) -> bool:
    sid = (sender_id or "").strip()
    if not sid:
        return False
    rules = load_rules()
    kept = [r for r in rules if r.get("sender_id") != sid]
    if len(kept) == len(rules):
        return False
    save_rules(kept)
    return True


def apply_rule_to_metrics(metrics: dict[str, Any], rule: dict[str, Any] | None) -> dict[str, Any]:
    """Honor local VIP/muted rules on categorization metrics."""
    from crawley.sender_inbox.schema import normalize_metrics

    m = normalize_metrics(metrics)
    if not rule:
        return m
    priority = rule.get("priority") or "normal"
    if priority == "vip":
        m["vip"] = True
        signals = list(m.get("signals") or [])
        if "vip" not in signals:
            signals.insert(0, "vip")
        m["signals"] = signals[:5]
    elif priority == "muted":
        m["vip"] = False
        # Soft deprioritize: never force high urgency from LLM alone for muted
        if m.get("urgency") in {"high", "critical"}:
            m["urgency"] = "medium"
        signals = [s for s in (m.get("signals") or []) if s != "vip"]
        if "muted" not in signals:
            signals.append("muted")
        m["signals"] = signals[:5]
    tags = rule.get("tags") or []
    if tags:
        signals = list(m.get("signals") or [])
        for tag in tags:
            if tag not in signals:
                signals.append(tag)
        m["signals"] = signals[:5]
    m["_rule_priority"] = priority
    return m


def rule_sort_boost(sender_id: str = "", *, from_addr: str = "") -> int:
    rule = get_rule(sender_id, from_addr=from_addr)
    if not rule:
        return 0
    if rule.get("priority") == "vip":
        return 50
    if rule.get("priority") == "muted":
        return -40
    return 0
