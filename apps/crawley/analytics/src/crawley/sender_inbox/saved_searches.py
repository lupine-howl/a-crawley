"""Named Gmail / Sender Inbox saved searches (Sprint 28 / B50)."""

from __future__ import annotations

import json
import re
import threading
import uuid
from datetime import UTC, datetime
from typing import Any

from crawley.data.paths import ensure_data_dirs
from crawley.sender_inbox.store import inbox_dir

_lock = threading.RLock()

MAX_RESULTS = 25
EXAMPLES = (
    "from:boss@example.com newer_than:30d",
    "subject:(invoice OR receipt) -unsubscribe",
    "label:INBOX is:unread",
)


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def searches_path():
    ensure_data_dirs()
    return inbox_dir() / "saved_searches.json"


def last_run_path():
    return inbox_dir() / "saved_search_last_run.json"


def load_searches() -> list[dict[str, Any]]:
    with _lock:
        path = searches_path()
        if not path.exists():
            return []
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        if not isinstance(raw, list):
            return []
        return [normalize_search(r) for r in raw if isinstance(r, dict)]


def save_searches(rows: list[dict[str, Any]]) -> None:
    with _lock:
        path = searches_path()
        cleaned = [normalize_search(r) for r in rows]
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(cleaned, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        tmp.replace(path)


def normalize_search(raw: dict[str, Any] | None) -> dict[str, Any]:
    data = raw if isinstance(raw, dict) else {}
    name = str(data.get("name") or "").strip()[:80]
    query = str(data.get("query") or "").strip()[:500]
    return {
        "id": str(data.get("id") or uuid.uuid4()),
        "name": name or "Untitled",
        "query": query,
        "updated_at": str(data.get("updated_at") or "") or _now_iso(),
    }


def upsert_search(*, search_id: str = "", name: str, query: str) -> dict[str, Any]:
    name = (name or "").strip()
    query = (query or "").strip()
    if not name:
        raise ValueError("Name is required.")
    if not query:
        raise ValueError("Query is required.")
    if len(query) > 500:
        raise ValueError("Query too long (max 500 chars).")
    # Soft validation: reject empty/control-only
    if not re.sub(r"\s+", "", query):
        raise ValueError("Query looks empty.")
    rows = load_searches()
    row = normalize_search(
        {
            "id": search_id or str(uuid.uuid4()),
            "name": name,
            "query": query,
            "updated_at": _now_iso(),
        }
    )
    out: list[dict[str, Any]] = []
    replaced = False
    for existing in rows:
        if existing.get("id") == row["id"]:
            out.append(row)
            replaced = True
        else:
            out.append(existing)
    if not replaced:
        out.append(row)
    save_searches(out)
    return row


def delete_search(search_id: str) -> bool:
    sid = (search_id or "").strip()
    if not sid:
        return False
    rows = load_searches()
    kept = [r for r in rows if r.get("id") != sid]
    if len(kept) == len(rows):
        return False
    save_searches(kept)
    return True


def get_search(search_id: str) -> dict[str, Any] | None:
    sid = (search_id or "").strip()
    for row in load_searches():
        if row.get("id") == sid:
            return row
    return None


def run_saved_search(creds, query: str, *, max_results: int = MAX_RESULTS) -> dict[str, Any]:
    """Bounded Gmail messages.list with operator query. Returns status payload."""
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError

    query = (query or "").strip()
    if not query:
        raise ValueError("Query is required.")
    service = build("gmail", "v1", credentials=creds, cache_discovery=False)
    try:
        listed = (
            service.users()
            .messages()
            .list(userId="me", q=query, maxResults=max(1, min(max_results, MAX_RESULTS)))
            .execute()
        )
    except HttpError as exc:
        status = getattr(exc.resp, "status", None)
        reason = exc.reason or str(exc)
        if status == 400:
            raise ValueError(f"Invalid Gmail query ({status}): {reason}") from exc
        raise RuntimeError(f"Gmail search failed ({status or '?'}): {reason}") from exc

    ids = [m["id"] for m in listed.get("messages", []) if m.get("id")]
    # Lightweight metadata for UI
    rows: list[dict[str, str]] = []
    for mid in ids[:MAX_RESULTS]:
        full = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=mid,
                format="metadata",
                metadataHeaders=["From", "Subject", "Date"],
            )
            .execute()
        )
        headers = {
            h.get("name", "").lower(): h.get("value", "")
            for h in (full.get("payload") or {}).get("headers", [])
        }
        rows.append(
            {
                "id": mid,
                "thread_id": str(full.get("threadId") or ""),
                "from": headers.get("from", ""),
                "subject": headers.get("subject", "(no subject)"),
                "snippet": (full.get("snippet") or "")[:200],
            }
        )
    result = {
        "status": "done",
        "query": query,
        "count": len(rows),
        "messages": rows,
        "error": "",
        "ran_at": _now_iso(),
    }
    with _lock:
        path = last_run_path()
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        tmp.replace(path)
    return result


def load_last_run() -> dict[str, Any] | None:
    path = last_run_path()
    if not path.exists():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return raw if isinstance(raw, dict) else None
