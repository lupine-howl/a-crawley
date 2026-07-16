"""Bounded ASX market + news fetches."""

from __future__ import annotations

import logging
import time
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from typing import Any
from urllib.parse import quote_plus

import httpx

from crawley.asx_desk.sources import enabled_source_ids
from crawley.modules.investment_fetch import USER_AGENT

logger = logging.getLogger(__name__)

HTTP_TIMEOUT = 12.0
RATE_LIMIT_S = 0.8


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def fetch_yahoo_snapshot(ticker: str) -> dict[str, Any]:
    """Last price / % change / volume via Yahoo chart for TICKER.AX."""
    symbol = f"{ticker.upper()}.AX"
    url = (
        "https://query1.finance.yahoo.com/v8/finance/chart/"
        f"{symbol}?interval=1d&range=5d"
    )
    gaps: list[str] = []
    try:
        with httpx.Client(timeout=HTTP_TIMEOUT, headers={"User-Agent": USER_AGENT}) as client:
            resp = client.get(url)
            resp.raise_for_status()
            payload = resp.json()
    except Exception as exc:  # noqa: BLE001
        logger.info("Yahoo chart failed for %s: %s", ticker, exc)
        return {
            "price": None,
            "change_pct": None,
            "volume": None,
            "currency": "AUD",
            "as_of": _now_iso(),
            "gaps": [f"yahoo_chart unavailable: {exc}"],
            "ok": False,
        }

    try:
        result = (payload.get("chart") or {}).get("result") or []
        if not result:
            raise ValueError("empty chart result")
        meta = result[0].get("meta") or {}
        price = meta.get("regularMarketPrice")
        prev = meta.get("chartPreviousClose") or meta.get("previousClose")
        volume = meta.get("regularMarketVolume")
        change_pct = None
        if price is not None and prev:
            change_pct = ((float(price) - float(prev)) / float(prev)) * 100.0
        if price is None:
            gaps.append("price unavailable")
        if change_pct is None:
            gaps.append("% move unavailable")
        if volume is None:
            gaps.append("volume unavailable")
        return {
            "price": float(price) if price is not None else None,
            "change_pct": float(change_pct) if change_pct is not None else None,
            "volume": float(volume) if volume is not None else None,
            "currency": meta.get("currency") or "AUD",
            "as_of": _now_iso(),
            "gaps": gaps,
            "ok": True,
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "price": None,
            "change_pct": None,
            "volume": None,
            "currency": "AUD",
            "as_of": _now_iso(),
            "gaps": [f"yahoo parse: {exc}"],
            "ok": False,
        }


def fetch_news_headlines(ticker: str, name: str, *, limit: int = 5) -> list[dict[str, str]]:
    query = f"{ticker} OR \"{name}\" ASX"
    url = (
        "https://news.google.com/rss/search?q="
        + quote_plus(query)
        + "&hl=en-AU&gl=AU&ceid=AU:en"
    )
    try:
        with httpx.Client(timeout=HTTP_TIMEOUT, headers={"User-Agent": USER_AGENT}) as client:
            resp = client.get(url)
            resp.raise_for_status()
            root = ET.fromstring(resp.content)
    except Exception as exc:  # noqa: BLE001
        logger.info("News RSS failed for %s: %s", ticker, exc)
        return []

    items: list[dict[str, str]] = []
    for item in root.findall("./channel/item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        if not title:
            continue
        items.append({"title": title[:240], "url": link})
        if len(items) >= limit:
            break
    return items


def scan_company(ticker: str, name: str) -> dict[str, Any]:
    """One polite scan: market snapshot + headlines. Honours enabled sources."""
    enabled = enabled_source_ids()
    sources_used: list[str] = []
    gaps: list[str] = []
    snapshot: dict[str, Any] = {
        "price": None,
        "change_pct": None,
        "volume": None,
        "currency": "AUD",
        "as_of": _now_iso(),
        "gaps": [],
        "sentiment": "unknown",
        "headline": "",
    }
    headlines: list[dict[str, str]] = []

    if "yahoo_chart" in enabled:
        sources_used.append("yahoo_chart")
        snap = fetch_yahoo_snapshot(ticker)
        snapshot.update({k: snap.get(k) for k in ("price", "change_pct", "volume", "currency", "as_of")})
        gaps.extend(snap.get("gaps") or [])
        time.sleep(RATE_LIMIT_S)
    else:
        gaps.append("yahoo_chart disabled")

    if "google_news_rss" in enabled:
        sources_used.append("google_news_rss")
        headlines = fetch_news_headlines(ticker, name)
        if headlines:
            snapshot["headline"] = headlines[0]["title"]
        else:
            gaps.append("no headlines")
        time.sleep(RATE_LIMIT_S)
    else:
        gaps.append("google_news_rss disabled")

    if "asx_announcements_hint" in enabled:
        sources_used.append("asx_announcements_hint")
        gaps.append("ASX announcements curated mode — no auto fetch configured")

    snapshot["gaps"] = gaps
    return {
        "ticker": ticker.upper(),
        "snapshot": snapshot,
        "headlines": headlines,
        "sources_used": sources_used,
        "scanned_at": _now_iso(),
    }
