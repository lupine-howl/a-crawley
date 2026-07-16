"""ASX active-set news theme clustering (Sprint 25 / B47)."""

from __future__ import annotations

import json
import logging
import threading
from datetime import UTC, datetime
from typing import Any

from crawley.data.paths import ensure_data_dirs

logger = logging.getLogger(__name__)

_lock = threading.RLock()
_job_lock = threading.Lock()
_running = False

# Hard caps — not a market-wide product.
MAX_HEADLINES = 80
MAX_PER_TICKER = 4
MAX_THEMES = 8
MAX_SOURCES_PER_THEME = 8

THEME_KEYWORDS: list[tuple[str, tuple[str, ...]]] = [
    ("Earnings & results", ("earn", "profit", "result", "guidance", "fy2", "1h", "2h", "npata", "ebit")),
    ("Dividends & capital", ("dividend", "buyback", "capital return", "franking", "payout")),
    ("Rates & macro", ("rba", "interest rate", "inflation", "gdp", "unemployment", "rate cut", "rate hike")),
    ("M&A / deals", ("acquire", "acquisition", "merger", "takeover", "bid", "deal")),
    ("Regulation & legal", ("regulator", "asic", "accc", "lawsuit", "fine", "compliance")),
    ("Commodities & energy", ("oil", "gas", "iron ore", "coal", "lithium", "copper", "gold", "commodity")),
    ("Banking & credit", ("loan", "mortgage", "credit", "deposit", "net interest")),
]


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _path():
    from crawley.data.paths import INVESTMENT_DIR

    ensure_data_dirs()
    root = INVESTMENT_DIR / "asx"
    root.mkdir(parents=True, exist_ok=True)
    return root / "news_clusters.json"


def default_clusters() -> dict[str, Any]:
    return {
        "status": "idle",  # idle | busy | ready | error | empty
        "themes": [],
        "summary": "",
        "markdown": "",
        "headline_count": 0,
        "ticker_count": 0,
        "method": "",  # heuristic | llm
        "updated_at": "",
        "error": "",
    }


def load_clusters() -> dict[str, Any]:
    with _lock:
        path = _path()
        if not path.exists():
            return default_clusters()
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return default_clusters()
        if not isinstance(raw, dict):
            return default_clusters()
        base = default_clusters()
        base.update(raw)
        base["themes"] = list(base.get("themes") or [])
        return base


def save_clusters(payload: dict[str, Any]) -> None:
    with _lock:
        path = _path()
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        tmp.replace(path)


def is_running() -> bool:
    return _running


def collect_active_headlines(
    *,
    max_headlines: int = MAX_HEADLINES,
    max_per_ticker: int = MAX_PER_TICKER,
) -> tuple[list[dict[str, Any]], int]:
    """Reuse scan headlines for active set; filter muted domains. Returns (rows, ticker_count)."""
    from crawley.asx_desk.citations import filter_muted_headlines
    from crawley.asx_desk.store import load_scan_state, load_scans

    state = load_scan_state()
    poc = list(state.get("poc_tickers") or [])
    scans = load_scans()
    rows: list[dict[str, Any]] = []
    for ticker in poc:
        scan = scans.get(ticker) or {}
        headlines = filter_muted_headlines(list(scan.get("headlines") or []))
        for h in headlines[: max(1, max_per_ticker)]:
            title = str(h.get("title") or "").strip()
            if not title:
                continue
            rows.append(
                {
                    "ticker": ticker,
                    "title": title[:300],
                    "url": str(h.get("url") or "").strip()[:500],
                    "published": str(h.get("published") or "").strip()[:40],
                }
            )
            if len(rows) >= max_headlines:
                return rows, len(poc)
    return rows, len(poc)


def _match_theme(title: str) -> str:
    lower = title.lower()
    for name, keys in THEME_KEYWORDS:
        if any(k in lower for k in keys):
            return name
    return "Other / general"


def cluster_headlines_heuristic(headlines: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keyword themes with source lists. Always available offline."""
    buckets: dict[str, list[dict[str, Any]]] = {}
    for h in headlines:
        theme = _match_theme(str(h.get("title") or ""))
        buckets.setdefault(theme, []).append(h)

    # Prefer named themes over Other; cap theme count.
    ordered_names = [n for n, _ in THEME_KEYWORDS if n in buckets]
    if "Other / general" in buckets:
        ordered_names.append("Other / general")

    themes: list[dict[str, Any]] = []
    for name in ordered_names[:MAX_THEMES]:
        sources = buckets[name][:MAX_SOURCES_PER_THEME]
        tickers = sorted({s.get("ticker") or "" for s in sources if s.get("ticker")})
        summary = (
            f"{len(sources)} headline(s) across {len(tickers)} ticker(s)"
            + (f" ({', '.join(tickers[:6])}{'…' if len(tickers) > 6 else ''})" if tickers else "")
        )
        themes.append(
            {
                "theme": name,
                "summary": summary,
                "sources": sources,
            }
        )
    return themes


def cluster_headlines_llm(headlines: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Ask LLM for themes; raises on failure so caller can fall back."""
    from crawley.llm.base import ChatMessage
    from crawley.llm.factory import get_llm_provider

    lines = []
    for i, h in enumerate(headlines[:MAX_HEADLINES]):
        lines.append(
            f"{i+1}. [{h.get('ticker')}] {h.get('title')}"
            + (f" ({h.get('url')})" if h.get("url") else "")
        )
    system = (
        "Cluster ASX news headlines into research themes for a personal operator. "
        "Reply with ONLY a JSON array (no markdown) of objects:\n"
        '[{"theme":"short name","summary":"one sentence","source_indexes":[1,2]}]\n'
        f"Max {MAX_THEMES} themes. Use only provided indexes. "
        "Themes are research aids — not trade signals or order recommendations."
    )
    user = "Headlines:\n" + "\n".join(lines)
    provider = get_llm_provider()
    result = provider.complete(
        [
            ChatMessage(role="system", content=system),
            ChatMessage(role="user", content=user),
        ],
        max_tokens=900,
    )
    text = (result.content or "").strip()
    try:
        raw = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("[")
        end = text.rfind("]")
        if start < 0 or end <= start:
            raise ValueError("No JSON array in clustering response") from None
        raw = json.loads(text[start : end + 1])
    if not isinstance(raw, list):
        raise ValueError("Clustering JSON must be an array")

    themes: list[dict[str, Any]] = []
    for item in raw[:MAX_THEMES]:
        if not isinstance(item, dict):
            continue
        name = str(item.get("theme") or "").strip()[:80]
        if not name:
            continue
        indexes = item.get("source_indexes") or item.get("sources") or []
        sources: list[dict[str, Any]] = []
        seen: set[str] = set()
        for idx in indexes:
            try:
                i = int(idx) - 1
            except (TypeError, ValueError):
                continue
            if i < 0 or i >= len(headlines):
                continue
            h = headlines[i]
            key = h.get("url") or h.get("title") or str(i)
            if key in seen:
                continue
            seen.add(str(key))
            sources.append(h)
            if len(sources) >= MAX_SOURCES_PER_THEME:
                break
        if not sources:
            continue
        themes.append(
            {
                "theme": name,
                "summary": str(item.get("summary") or "").strip()[:300],
                "sources": sources,
            }
        )
    if not themes:
        raise ValueError("LLM returned no usable themes")
    return themes


def themes_to_markdown(themes: list[dict[str, Any]], *, method: str, headline_count: int) -> str:
    lines = [
        "# ASX news themes",
        "",
        f"Method: {method} · headlines: {headline_count} · research aid only — not trade signals.",
        "",
    ]
    if not themes:
        lines.append("_No themes — empty active-set headlines or all muted._")
        return "\n".join(lines)
    for t in themes:
        lines.append(f"## {t.get('theme')}")
        if t.get("summary"):
            lines.append("")
            lines.append(str(t["summary"]))
        lines.append("")
        for s in t.get("sources") or []:
            title = (s.get("title") or "").replace("\n", " ")
            url = s.get("url") or ""
            ticker = s.get("ticker") or ""
            if url:
                lines.append(f"- **{ticker}** — [{title}]({url})")
            else:
                lines.append(f"- **{ticker}** — {title}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def build_clusters(*, prefer_llm: bool = True) -> dict[str, Any]:
    """Collect + cluster; LLM preferred when available, heuristic fallback."""
    headlines, ticker_count = collect_active_headlines()
    if not headlines:
        payload = default_clusters()
        payload.update(
            {
                "status": "empty",
                "summary": "No headlines on the active set yet — run a desk scan first.",
                "ticker_count": ticker_count,
                "updated_at": _now_iso(),
                "markdown": themes_to_markdown([], method="none", headline_count=0),
            }
        )
        return payload

    method = "heuristic"
    themes: list[dict[str, Any]]
    if prefer_llm:
        try:
            themes = cluster_headlines_llm(headlines)
            method = "llm"
        except Exception as exc:  # noqa: BLE001
            logger.info("LLM clustering unavailable (%s); using heuristic", exc)
            themes = cluster_headlines_heuristic(headlines)
    else:
        themes = cluster_headlines_heuristic(headlines)

    summary = (
        f"{len(themes)} theme(s) from {len(headlines)} headline(s) "
        f"across {ticker_count} active ticker(s) ({method})."
    )
    return {
        "status": "ready",
        "themes": themes,
        "summary": summary,
        "markdown": themes_to_markdown(themes, method=method, headline_count=len(headlines)),
        "headline_count": len(headlines),
        "ticker_count": ticker_count,
        "method": method,
        "updated_at": _now_iso(),
        "error": "",
    }


def start_cluster_refresh(executor, *, prefer_llm: bool = True) -> tuple[bool, str]:
    global _running
    from crawley.asx_desk.store import load_scan_state

    poc = list(load_scan_state().get("poc_tickers") or [])
    if not poc:
        return False, "Active set is empty — configure tickers first."
    with _job_lock:
        if _running:
            return False, "Theme clustering already running."
        _running = True
        payload = load_clusters()
        payload["status"] = "busy"
        payload["error"] = ""
        save_clusters(payload)

    def _body() -> None:
        global _running
        try:
            result = build_clusters(prefer_llm=prefer_llm)
            save_clusters(result)
        except Exception as exc:  # noqa: BLE001
            logger.exception("News clustering failed")
            payload = load_clusters()
            payload["status"] = "error"
            payload["error"] = str(exc)[:300]
            payload["updated_at"] = _now_iso()
            save_clusters(payload)
        finally:
            with _job_lock:
                _running = False

    executor.submit(_body)
    return True, "Clustering active-set headlines…"
