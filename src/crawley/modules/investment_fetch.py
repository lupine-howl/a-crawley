"""Bounded investment search/fetch helpers."""

from __future__ import annotations

import re
import uuid
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import quote_plus

import httpx

from crawley.data.duck import duck_connection
from crawley.data.paths import INVESTMENT_DIR, ensure_data_dirs

MAX_ITEMS = 3
MAX_PAGE_BYTES = 40_000
MAX_RSS_BYTES = 512_000
HTTP_TIMEOUT = 12.0
USER_AGENT = "CrawleyPersonalAssistant/0.1 (+local; lite investment PoC)"


class InvestmentFetchError(Exception):
    """User-visible failure while fetching investment sources."""


def _strip_html(text: str) -> str:
    text = re.sub(r"(?is)<script.*?>.*?</script>", " ", text)
    text = re.sub(r"(?is)<style.*?>.*?</style>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def parse_rss_items(raw: bytes | str, *, limit: int = MAX_ITEMS) -> list[dict[str, str]]:
    """Parse RSS/Atom-ish Google News XML into title/url/snippet dicts."""
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        raise InvestmentFetchError(
            f"News feed XML could not be parsed (feed may be truncated or blocked): {exc}"
        ) from exc

    items: list[dict[str, str]] = []
    for item in root.findall("./channel/item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        description = (item.findtext("description") or "").strip()
        if not title or not link:
            continue
        items.append(
            {
                "title": title,
                "url": link,
                "snippet": _strip_html(description)[:500],
            }
        )
        if len(items) >= limit:
            break
    return items


def fetch_rss_items(query: str, *, limit: int = MAX_ITEMS) -> list[dict[str, str]]:
    """Pull a few Google News RSS entries for the query (bounded item count)."""
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
        raise InvestmentFetchError(f"News feed request failed: {exc}") from exc

    if len(content) > MAX_RSS_BYTES:
        # Prefer failing clearly over silently truncating mid-XML.
        raise InvestmentFetchError(
            f"News feed exceeded {MAX_RSS_BYTES} bytes; refusing to truncate XML."
        )

    return parse_rss_items(content, limit=limit)


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
    """Write raw snippets to data/ and DuckDB; return rows for LLM."""
    ensure_data_dirs()
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    run_dir = INVESTMENT_DIR / stamp
    run_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(UTC).replace(tzinfo=None)
    rows: list[dict[str, str]] = []

    with duck_connection() as con:
        for index, item in enumerate(items, start=1):
            body = item.get("body") or item.get("snippet") or ""
            if item.get("url") and not item.get("body"):
                try:
                    body = fetch_page_text(item["url"])
                except Exception as exc:  # noqa: BLE001 — keep run going for other sources
                    body = f"{item.get('snippet', '')}\n[fetch error: {exc}]"

            artifact_path = run_dir / f"{index}.txt"
            artifact_path.write_text(
                f"title: {item['title']}\nurl: {item['url']}\n\n{body}\n",
                encoding="utf-8",
            )
            row_id = str(uuid.uuid4())
            snippet = (item.get("snippet") or body)[:500]
            con.execute(
                """
                INSERT INTO investment_artifacts
                (id, fetched_at, query, source_url, title, artifact_path, snippet)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    row_id,
                    now,
                    query,
                    item["url"],
                    item["title"],
                    str(artifact_path),
                    snippet,
                ],
            )
            rows.append(
                {
                    "id": row_id,
                    "title": item["title"],
                    "url": item["url"],
                    "snippet": snippet,
                    "artifact_path": str(artifact_path),
                }
            )
    return rows


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
