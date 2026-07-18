"""Bounded investment search/fetch helpers with optional query cache."""

from __future__ import annotations

import hashlib
import json
import re
import uuid
import xml.etree.ElementTree as ET
from datetime import UTC, datetime, timedelta
from pathlib import Path
from urllib.parse import quote_plus

import httpx

from crawley.data.duck import duck_connection
from crawley.data.paths import INVESTMENT_DIR, ensure_data_dirs

MAX_ITEMS = 5
MAX_PAGE_BYTES = 40_000
MAX_RSS_BYTES = 512_000
HTTP_TIMEOUT = 12.0
CACHE_TTL = timedelta(hours=1)
USER_AGENT = "CrawleyPersonalAssistant/0.1 (+local; lite investment PoC)"


class InvestmentFetchError(Exception):
    """User-visible failure while fetching investment sources."""


class InvestmentParseError(InvestmentFetchError):
    """Feed returned but could not be parsed."""


class InvestmentNetworkError(InvestmentFetchError):
    """Network / HTTP failure contacting a source."""


class InvestmentEmptyError(InvestmentFetchError):
    """Sources returned nothing useful."""


def _strip_html(text: str) -> str:
    text = re.sub(r"(?is)<script.*?>.*?</script>", " ", text)
    text = re.sub(r"(?is)<style.*?>.*?</style>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def query_cache_key(query: str) -> str:
    normalized = " ".join(query.strip().lower().split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:24]


def _cache_path(query: str) -> Path:
    return INVESTMENT_DIR / "cache" / f"{query_cache_key(query)}.json"


def load_cached_items(query: str) -> tuple[list[dict[str, str]], str] | None:
    """Return (items, cached_at_iso) if a fresh cache hit exists."""
    path = _cache_path(query)
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        cached_at = datetime.fromisoformat(payload["cached_at"])
        if cached_at.tzinfo is None:
            cached_at = cached_at.replace(tzinfo=UTC)
        if datetime.now(UTC) - cached_at > CACHE_TTL:
            return None
        items = payload.get("items") or []
        if not items:
            return None
        return items, cached_at.isoformat()
    except (OSError, json.JSONDecodeError, KeyError, ValueError):
        return None


def save_cached_items(query: str, items: list[dict[str, str]]) -> None:
    ensure_data_dirs()
    path = _cache_path(query)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "query": query,
                "cached_at": datetime.now(UTC).isoformat(),
                "items": items,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def parse_rss_items(raw: bytes | str, *, limit: int = MAX_ITEMS) -> list[dict[str, str]]:
    """Parse RSS/Atom-ish Google News XML into title/url/snippet dicts."""
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        raise InvestmentParseError(
            f"News feed XML could not be parsed (feed may be truncated or blocked): {exc}"
        ) from exc

    items: list[dict[str, str]] = []
    for item in root.findall("./channel/item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        description = (item.findtext("description") or "").strip()
        pub = (item.findtext("pubDate") or "").strip()
        source_el = item.find("source")
        source_name = (source_el.text or "").strip() if source_el is not None else ""
        if not title or not link:
            continue
        items.append(
            {
                "title": title,
                "url": link,
                "snippet": _strip_html(description)[:500],
                "published": pub,
                "publisher": source_name,
            }
        )
        if len(items) >= limit:
            break
    return items


def fetch_rss_items(
    query: str,
    *,
    limit: int = MAX_ITEMS,
    use_cache: bool = True,
) -> tuple[list[dict[str, str]], dict[str, str]]:
    """
    Pull Google News RSS entries (bounded).

    Returns (items, meta) where meta may include cache_hit / cached_at.
    """
    if use_cache:
        hit = load_cached_items(query)
        if hit is not None:
            items, cached_at = hit
            return items[:limit], {"cache_hit": "true", "cached_at": cached_at}

    url = (
        "https://news.google.com/rss/search?"
        f"q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"
    )
    try:
        with httpx.Client(
            timeout=HTTP_TIMEOUT,
            follow_redirects=True,
            headers={"User-Agent": USER_AGENT},
        ) as client:
            response = client.get(url)
            response.raise_for_status()
            content = response.content
    except httpx.HTTPError as exc:
        raise InvestmentNetworkError(f"News feed request failed: {exc}") from exc

    if len(content) > MAX_RSS_BYTES:
        raise InvestmentFetchError(
            f"News feed exceeded {MAX_RSS_BYTES} bytes; refusing to truncate XML."
        )

    items = parse_rss_items(content, limit=limit)
    if not items:
        raise InvestmentEmptyError(
            "News feed returned no usable headlines. Try a different query."
        )
    save_cached_items(query, items)
    return items, {"cache_hit": "false"}


def fetch_page_text(url: str) -> str:
    with httpx.Client(
        timeout=HTTP_TIMEOUT,
        follow_redirects=True,
        headers={"User-Agent": USER_AGENT},
    ) as client:
        response = client.get(url)
        response.raise_for_status()
        text = response.text[:MAX_PAGE_BYTES]
    return _strip_html(text)[:8000]


def persist_artifacts(query: str, items: list[dict[str, str]]) -> list[dict[str, str]]:
    """Write raw snippets to data/ and DuckDB; return rows for LLM.

    Network fetches happen before opening DuckDB so status polls never share a
    live connection with long-running HTTP work.
    """
    ensure_data_dirs()
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    run_dir = INVESTMENT_DIR / stamp
    run_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(UTC).replace(tzinfo=None)

    prepared: list[dict[str, str]] = []
    for index, item in enumerate(items, start=1):
        body = item.get("body") or item.get("snippet") or ""
        if item.get("url") and not item.get("body"):
            try:
                body = fetch_page_text(item["url"])
            except Exception as exc:  # noqa: BLE001 — keep run going for other sources
                body = f"{item.get('snippet', '')}\n[fetch error: {exc}]"

        artifact_path = run_dir / f"{index}.txt"
        meta_bits = []
        if item.get("publisher"):
            meta_bits.append(f"publisher: {item['publisher']}")
        if item.get("published"):
            meta_bits.append(f"published: {item['published']}")
        header = f"title: {item['title']}\nurl: {item['url']}\n"
        if meta_bits:
            header += "\n".join(meta_bits) + "\n"
        artifact_path.write_text(f"{header}\n{body}\n", encoding="utf-8")
        snippet = (item.get("snippet") or body)[:500]
        prepared.append(
            {
                "id": str(uuid.uuid4()),
                "title": item["title"],
                "url": item["url"],
                "snippet": snippet,
                "artifact_path": str(artifact_path),
                "publisher": item.get("publisher") or "",
                "published": item.get("published") or "",
            }
        )

    with duck_connection() as con:
        for row in prepared:
            con.execute(
                """
                INSERT INTO investment_artifacts
                (id, fetched_at, query, source_url, title, artifact_path, snippet)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    row["id"],
                    now,
                    query,
                    row["url"],
                    row["title"],
                    row["artifact_path"],
                    row["snippet"],
                ],
            )
    return prepared


def recent_artifacts(limit: int = 5) -> list[dict]:
    try:
        with duck_connection(read_only=True) as con:
            result = con.execute(
                """
                SELECT title, source_url, snippet, fetched_at
                FROM investment_artifacts
                ORDER BY fetched_at DESC
                LIMIT ?
                """,
                [limit],
            ).fetchall()
    except Exception:  # noqa: BLE001 — empty DB / first run
        return []
    return [
        {
            "title": r[0],
            "url": r[1],
            "snippet": r[2],
            "fetched_at": str(r[3]),
        }
        for r in result
    ]


def artifact_dir_for(path: str | Path) -> Path:
    return Path(path)
