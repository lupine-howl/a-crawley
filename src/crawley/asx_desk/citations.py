"""ASX structured citations + domain mute (Sprint 30 / B53)."""

from __future__ import annotations

import json
import threading
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlparse

from crawley.data.paths import ensure_data_dirs

_lock = threading.RLock()

QUALITY_TAGS = ("trusted", "ok", "low", "unknown")

# Simple quality rubric (also documented in architecture):
# trusted = operator-marked or official-looking domain
# ok = normal news domain
# low = aggregator / thin / previously muted context
# unknown = default


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _root():
    from crawley.data.paths import INVESTMENT_DIR

    ensure_data_dirs()
    path = INVESTMENT_DIR / "asx"
    path.mkdir(parents=True, exist_ok=True)
    return path


def citations_path():
    return _root() / "citations.json"


def muted_domains_path():
    return _root() / "muted_domains.json"


def domain_of(url: str) -> str:
    try:
        host = (urlparse(url or "").hostname or "").lower().rstrip(".")
    except Exception:  # noqa: BLE001
        return ""
    if host.startswith("www."):
        host = host[4:]
    return host


def load_muted_domains() -> list[str]:
    with _lock:
        path = muted_domains_path()
        if not path.exists():
            return []
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        if isinstance(raw, list):
            return sorted({str(d).lower().strip() for d in raw if str(d).strip()})
        return []


def save_muted_domains(domains: list[str]) -> None:
    with _lock:
        path = muted_domains_path()
        cleaned = sorted({str(d).lower().strip() for d in domains if str(d).strip()})
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(cleaned, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        tmp.replace(path)


def mute_domain(domain: str) -> list[str]:
    d = domain_of(domain) if "://" in (domain or "") else (domain or "").lower().strip()
    if not d:
        raise ValueError("Domain required")
    domains = load_muted_domains()
    if d not in domains:
        domains.append(d)
    save_muted_domains(domains)
    return domains


def unmute_domain(domain: str) -> list[str]:
    d = domain_of(domain) if "://" in (domain or "") else (domain or "").lower().strip()
    domains = [x for x in load_muted_domains() if x != d]
    save_muted_domains(domains)
    return domains


def is_muted_url(url: str) -> bool:
    host = domain_of(url)
    muted = set(load_muted_domains())
    if not host:
        return False
    return host in muted or any(host.endswith("." + m) for m in muted)


def load_citations() -> list[dict[str, Any]]:
    with _lock:
        path = citations_path()
        if not path.exists():
            return []
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        if not isinstance(raw, list):
            return []
        return [normalize_citation(r) for r in raw if isinstance(r, dict)]


def save_citations(rows: list[dict[str, Any]]) -> None:
    with _lock:
        path = citations_path()
        # Cap growth
        cleaned = [normalize_citation(r) for r in rows][-500:]
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(cleaned, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        tmp.replace(path)


def normalize_citation(raw: dict[str, Any] | None) -> dict[str, Any]:
    data = raw if isinstance(raw, dict) else {}
    quality = str(data.get("quality") or "unknown").lower().strip()
    if quality not in QUALITY_TAGS:
        quality = "unknown"
    url = str(data.get("url") or "").strip()
    return {
        "url": url[:500],
        "title": str(data.get("title") or "").strip()[:300],
        "ticker": str(data.get("ticker") or "").strip().upper()[:12],
        "domain": domain_of(url) or str(data.get("domain") or "").lower()[:120],
        "retrieved_at": str(data.get("retrieved_at") or "") or _now_iso(),
        "quality": quality,
    }


def record_headlines_as_citations(
    ticker: str,
    headlines: list[dict[str, Any]],
    *,
    quality: str = "ok",
) -> list[dict[str, Any]]:
    """Persist structured source records from a scan; skip muted domains."""
    ticker = (ticker or "").strip().upper()
    existing = load_citations()
    by_url = {c.get("url"): c for c in existing if c.get("url")}
    added: list[dict[str, Any]] = []
    for h in headlines or []:
        url = str(h.get("url") or "").strip()
        title = str(h.get("title") or "").strip()
        if not url and not title:
            continue
        if url and is_muted_url(url):
            continue
        row = normalize_citation(
            {
                "url": url,
                "title": title,
                "ticker": ticker,
                "retrieved_at": _now_iso(),
                "quality": quality,
            }
        )
        if row["url"]:
            by_url[row["url"]] = row
        added.append(row)
    save_citations(list(by_url.values())[-500:])
    return added


def filter_muted_headlines(headlines: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [h for h in (headlines or []) if not is_muted_url(str(h.get("url") or ""))]


def citations_markdown_section(
    ticker: str = "",
    headlines: list[dict[str, Any]] | None = None,
    *,
    limit: int = 6,
) -> str:
    """Markdown citations block for profile/recommend output."""
    lines: list[str] = []
    seen: set[str] = set()
    for h in headlines or []:
        title = str(h.get("title") or "").strip()
        url = str(h.get("url") or "").strip()
        if is_muted_url(url):
            continue
        key = url or title
        if not key or key in seen:
            continue
        seen.add(key)
        domain = domain_of(url)
        if url:
            lines.append(f"- [{title or domain or 'source'}]({url})" + (f" · `{domain}`" if domain else ""))
        else:
            lines.append(f"- {title}")
        if len(lines) >= limit:
            break
    if not lines and ticker:
        for c in load_citations():
            if c.get("ticker") != ticker.upper():
                continue
            if c.get("domain") in set(load_muted_domains()):
                continue
            title = c.get("title") or c.get("domain") or "source"
            url = c.get("url") or ""
            key = url or title
            if key in seen:
                continue
            seen.add(key)
            if url:
                lines.append(f"- [{title}]({url}) · `{c.get('domain')}` · {c.get('quality')}")
            else:
                lines.append(f"- {title}")
            if len(lines) >= limit:
                break
    if not lines:
        return ""
    return "## Citations\n\n" + "\n".join(lines) + "\n"


def quality_rubric_text() -> str:
    return (
        "Citation quality tags: **trusted** (operator-preferred / official), "
        "**ok** (normal news), **low** (thin/aggregator), **unknown** (default). "
        "Muted domains are excluded from future scan headline use and citation prompts."
    )
