"""Configurable ASX source registry (Sprint 13 / B74)."""

from __future__ import annotations

import json
import threading
from copy import deepcopy
from pathlib import Path
from typing import Any

from crawley.data.paths import ensure_data_dirs

_lock = threading.RLock()

# Documented defaults — free/bounded, no TOS-hostile scraping targets.
DEFAULT_SOURCES: list[dict[str, Any]] = [
    {
        "id": "yahoo_chart",
        "name": "Yahoo Finance chart (*.AX)",
        "kind": "market_data",
        "mode": "scan",
        "enabled": True,
        "notes": "Unofficial quote chart endpoint for last price / % move / volume. Gaps expected.",
    },
    {
        "id": "google_news_rss",
        "name": "Google News RSS (ticker query)",
        "kind": "news",
        "mode": "scan",
        "enabled": True,
        "notes": "Bounded headlines for sentiment input; not an official ASX feed.",
    },
    {
        "id": "asx_announcements_hint",
        "name": "ASX announcements (manual / curated)",
        "kind": "filings",
        "mode": "curated",
        "enabled": False,
        "notes": "Placeholder — enable when a TOS-safe feed/API is configured. Not auto-scraped.",
    },
]

DEFAULT_PROMPTS: dict[str, str] = {
    "scan_system": (
        "You extract a one-line market read and sentiment for an ASX equity from "
        "bounded price+headline inputs. Reply with ONLY JSON: "
        '{"sentiment":"constructive|mixed|cautious|negative|unknown","headline":"…","brief":"…"}'
    ),
    "profile_system": (
        "You write a concise Markdown company profile for a personal ASX research desk. "
        "Sections: Business, Recent move, Sentiment, Risks / watch. "
        "Use only provided facts; show gaps honestly. Not licensed research or advice. "
        "Under 320 words."
    ),
    "sentiment_system": (
        "Classify overall news tone for one ASX ticker from headlines. "
        "Reply with ONLY JSON: "
        '{"sentiment":"constructive|mixed|cautious|negative|unknown","rationale":"one line"}'
    ),
}


def _config_path() -> Path:
    from crawley.data.paths import INVESTMENT_DIR

    ensure_data_dirs()
    path = INVESTMENT_DIR / "asx"
    path.mkdir(parents=True, exist_ok=True)
    return path / "sources_config.json"


def default_config() -> dict[str, Any]:
    return {
        "sources": deepcopy(DEFAULT_SOURCES),
        "prompts": dict(DEFAULT_PROMPTS),
    }


def load_config() -> dict[str, Any]:
    with _lock:
        path = _config_path()
        cfg = default_config()
        if not path.exists():
            return cfg
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return cfg
        if isinstance(raw.get("sources"), list) and raw["sources"]:
            cfg["sources"] = raw["sources"]
        if isinstance(raw.get("prompts"), dict):
            merged = dict(DEFAULT_PROMPTS)
            merged.update({k: str(v) for k, v in raw["prompts"].items() if v is not None})
            cfg["prompts"] = merged
        return cfg


def save_config(cfg: dict[str, Any]) -> None:
    with _lock:
        path = _config_path()
        path.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def enabled_source_ids() -> set[str]:
    return {s["id"] for s in load_config()["sources"] if s.get("enabled") and s.get("id")}


def set_source_enabled(source_id: str, enabled: bool) -> dict[str, Any]:
    cfg = load_config()
    for row in cfg["sources"]:
        if row.get("id") == source_id:
            row["enabled"] = bool(enabled)
    save_config(cfg)
    return cfg


def update_prompts(**fields: str) -> dict[str, Any]:
    cfg = load_config()
    prompts = dict(cfg.get("prompts") or DEFAULT_PROMPTS)
    for key, val in fields.items():
        if key in DEFAULT_PROMPTS and val is not None:
            prompts[key] = str(val)
    cfg["prompts"] = prompts
    save_config(cfg)
    return cfg
