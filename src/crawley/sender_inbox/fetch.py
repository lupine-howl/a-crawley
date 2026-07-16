"""Fetch a single Gmail message for Sender Inbox ingest."""

from __future__ import annotations

import base64
import re
from datetime import UTC, datetime
from email.utils import parseaddr
from typing import Any

from googleapiclient.discovery import build

from crawley.sender_inbox.schema import sender_id_for


def _header_map(payload_headers: list[dict[str, str]]) -> dict[str, str]:
    return {h.get("name", "").lower(): h.get("value", "") for h in payload_headers}


def _decode_part(data: str) -> str:
    if not data:
        return ""
    padded = data + "=" * (-len(data) % 4)
    try:
        return base64.urlsafe_b64decode(padded.encode("ascii")).decode("utf-8", errors="replace")
    except (ValueError, UnicodeError):
        return ""


def _walk_parts(payload: dict[str, Any], texts: list[str], htmls: list[str]) -> None:
    mime = (payload.get("mimeType") or "").lower()
    body = payload.get("body") or {}
    data = body.get("data") or ""
    if mime == "text/plain" and data:
        texts.append(_decode_part(data))
    elif mime == "text/html" and data:
        htmls.append(_decode_part(data))
    for part in payload.get("parts") or []:
        _walk_parts(part, texts, htmls)


_TAG_RE = re.compile(r"<[^>]+>")


def _html_to_text(html: str) -> str:
    text = _TAG_RE.sub(" ", html)
    return re.sub(r"\s+", " ", text).strip()


def extract_body_text(payload: dict[str, Any], *, max_chars: int = 4000) -> str:
    texts: list[str] = []
    htmls: list[str] = []
    _walk_parts(payload or {}, texts, htmls)
    body = "\n\n".join(t.strip() for t in texts if t.strip())
    if not body and htmls:
        body = _html_to_text("\n".join(htmls))
    body = body.strip()
    if len(body) > max_chars:
        body = body[: max_chars - 1] + "…"
    return body


def list_candidate_ids(creds, *, max_results: int = 50) -> list[str]:
    service = build("gmail", "v1", credentials=creds, cache_discovery=False)
    listed = (
        service.users()
        .messages()
        .list(userId="me", labelIds=["INBOX"], maxResults=max_results)
        .execute()
    )
    return [m["id"] for m in listed.get("messages", []) if m.get("id")]


def fetch_thread_messages(
    creds,
    thread_id: str,
    *,
    max_messages: int = 12,
    max_body_chars: int = 3500,
) -> list[dict[str, Any]]:
    """Fetch a bounded Gmail thread (newest first). No full-mailbox sync."""
    thread_id = (thread_id or "").strip()
    if not thread_id:
        return []
    service = build("gmail", "v1", credentials=creds, cache_discovery=False)
    full = (
        service.users()
        .threads()
        .get(userId="me", id=thread_id, format="full")
        .execute()
    )
    rows: list[dict[str, Any]] = []
    for msg in full.get("messages") or []:
        headers = _header_map((msg.get("payload") or {}).get("headers", []))
        from_raw = headers.get("from", "")
        from_name, from_addr = parseaddr(from_raw)
        from_addr = from_addr or from_raw
        subject = headers.get("subject", "(no subject)")
        snippet = (msg.get("snippet") or "").strip()
        internal_ms = int(msg.get("internalDate", "0") or "0")
        if internal_ms:
            internal_dt = datetime.fromtimestamp(internal_ms / 1000, tz=UTC)
            internal_iso = internal_dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")
        else:
            internal_iso = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        body = extract_body_text(msg.get("payload") or {}, max_chars=max_body_chars)
        rows.append(
            {
                "id": msg.get("id") or "",
                "thread_id": thread_id,
                "from_name": from_name or "",
                "from_addr": from_addr or "",
                "sender_id": sender_id_for(from_addr),
                "subject": subject,
                "snippet": snippet[:500],
                "body_text": body,
                "internal_date": internal_iso,
            }
        )
    rows.sort(key=lambda m: m.get("internal_date") or "", reverse=True)
    return rows[: max(1, max_messages)]


def fetch_message(creds, message_id: str) -> dict[str, Any]:
    """Return a normalized message dict ready for categorization."""
    service = build("gmail", "v1", credentials=creds, cache_discovery=False)
    full = (
        service.users()
        .messages()
        .get(userId="me", id=message_id, format="full")
        .execute()
    )
    headers = _header_map(full.get("payload", {}).get("headers", []))
    from_raw = headers.get("from", "")
    from_name, from_addr = parseaddr(from_raw)
    from_addr = from_addr or from_raw
    subject = headers.get("subject", "(no subject)")
    snippet = (full.get("snippet") or "").strip()
    internal_ms = int(full.get("internalDate", "0") or "0")
    if internal_ms:
        internal_dt = datetime.fromtimestamp(internal_ms / 1000, tz=UTC)
        internal_iso = internal_dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")
    else:
        internal_iso = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    body = extract_body_text(full.get("payload") or {})
    return {
        "id": message_id,
        "thread_id": full.get("threadId") or "",
        "from_name": from_name or "",
        "from_addr": from_addr or "",
        "sender_id": sender_id_for(from_addr),
        "subject": subject,
        "snippet": snippet[:500],
        "body_text": body,
        "internal_date": internal_iso,
        "metrics": {},
        "error": None,
        "ingested_at": "",
    }
