"""Attachment metadata + opt-in text extract (Sprint 29 / B52)."""

from __future__ import annotations

import base64
import json
import re
import threading
from datetime import UTC, datetime
from typing import Any

from crawley.data.paths import ensure_data_dirs
from crawley.sender_inbox.store import inbox_dir

_lock = threading.RLock()

ALLOWLIST_MIME = frozenset(
    {
        "text/plain",
        "text/csv",
        "text/markdown",
        "application/json",
        "message/rfc822",
    }
)
ALLOWLIST_EXT = frozenset({".txt", ".csv", ".md", ".json", ".log"})
MAX_EXTRACT_BYTES = 64_000
MAX_SNIPPET_CHARS = 2000


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def extracts_dir():
    ensure_data_dirs()
    path = inbox_dir() / "attachment_extracts"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _walk_attachments(payload: dict[str, Any], found: list[dict[str, Any]]) -> None:
    if not payload:
        return
    filename = str(payload.get("filename") or "").strip()
    body = payload.get("body") or {}
    mime = str(payload.get("mimeType") or "").lower()
    size = int(body.get("size") or 0)
    att_id = body.get("attachmentId") or ""
    if filename or att_id:
        found.append(
            {
                "filename": filename or "(unnamed)",
                "mime_type": mime,
                "size": size,
                "attachment_id": att_id,
                "part_id": str(payload.get("partId") or ""),
            }
        )
    for part in payload.get("parts") or []:
        _walk_attachments(part, found)


def list_attachments_from_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    _walk_attachments(payload or {}, found)
    # Deduplicate by attachment_id/filename
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for row in found:
        key = row.get("attachment_id") or f"{row.get('filename')}:{row.get('size')}"
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
    return out


def skip_reason(att: dict[str, Any]) -> str | None:
    """Return reason if attachment should not be auto-extracted."""
    mime = str(att.get("mime_type") or "").lower()
    name = str(att.get("filename") or "").lower()
    size = int(att.get("size") or 0)
    if size > MAX_EXTRACT_BYTES:
        return f"too large ({size} bytes; cap {MAX_EXTRACT_BYTES})"
    ext_ok = any(name.endswith(ext) for ext in ALLOWLIST_EXT)
    mime_ok = mime in ALLOWLIST_MIME or mime.startswith("text/")
    if not (ext_ok or mime_ok):
        return f"type not allowlisted ({mime or 'unknown'})"
    if not att.get("attachment_id"):
        return "inline/no attachment id"
    return None


def fetch_message_attachments(creds, message_id: str) -> list[dict[str, Any]]:
    from googleapiclient.discovery import build

    service = build("gmail", "v1", credentials=creds, cache_discovery=False)
    full = (
        service.users()
        .messages()
        .get(userId="me", id=message_id, format="full")
        .execute()
    )
    rows = list_attachments_from_payload(full.get("payload") or {})
    for row in rows:
        reason = skip_reason(row)
        row["extractable"] = reason is None
        row["skip_reason"] = reason or ""
        row["message_id"] = message_id
    return rows


def extract_attachment_text(
    creds,
    message_id: str,
    attachment_id: str,
    *,
    filename: str = "",
) -> dict[str, Any]:
    """Opt-in extract; never auto-called. Stores under data/."""
    from googleapiclient.discovery import build

    message_id = (message_id or "").strip()
    attachment_id = (attachment_id or "").strip()
    if not message_id or not attachment_id:
        raise ValueError("message_id and attachment_id required")

    # Re-check allowlist via metadata
    atts = fetch_message_attachments(creds, message_id)
    target = next((a for a in atts if a.get("attachment_id") == attachment_id), None)
    if target is None:
        raise ValueError("Attachment not found on message.")
    reason = skip_reason(target)
    if reason:
        raise ValueError(f"Skipped: {reason}")

    service = build("gmail", "v1", credentials=creds, cache_discovery=False)
    att = (
        service.users()
        .messages()
        .attachments()
        .get(userId="me", messageId=message_id, id=attachment_id)
        .execute()
    )
    data = att.get("data") or ""
    padded = data + "=" * (-len(data) % 4)
    try:
        raw = base64.urlsafe_b64decode(padded.encode("ascii"))
    except (ValueError, UnicodeError) as exc:
        raise ValueError(f"Could not decode attachment: {exc}") from exc
    if len(raw) > MAX_EXTRACT_BYTES:
        raise ValueError(f"Decoded size exceeds cap ({MAX_EXTRACT_BYTES}).")
    try:
        text = raw.decode("utf-8", errors="replace")
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"Not valid text: {exc}") from exc
    text = re.sub(r"\s+", " ", text).strip()[:MAX_SNIPPET_CHARS]
    record = {
        "message_id": message_id,
        "attachment_id": attachment_id,
        "filename": filename or target.get("filename") or "",
        "mime_type": target.get("mime_type") or "",
        "size": target.get("size") or len(raw),
        "text": text,
        "extracted_at": _now_iso(),
    }
    safe_name = re.sub(r"[^a-zA-Z0-9._-]+", "_", record["filename"])[:60] or "part"
    path = extracts_dir() / f"{message_id}_{safe_name}.json"
    with _lock:
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        tmp.replace(path)
    return record


def load_extracts_for_message(message_id: str) -> list[dict[str, Any]]:
    mid = (message_id or "").strip()
    if not mid:
        return []
    out: list[dict[str, Any]] = []
    for path in extracts_dir().glob(f"{mid}_*.json"):
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(raw, dict):
            out.append(raw)
    return out


def attachment_digest_slice(message_ids: list[str], *, max_chars: int = 1200) -> str:
    lines: list[str] = []
    for mid in message_ids[:8]:
        for row in load_extracts_for_message(mid):
            snippet = (row.get("text") or "")[:400]
            if not snippet:
                continue
            lines.append(f"- {row.get('filename')}: {snippet}")
    if not lines:
        return ""
    text = "Opt-in attachment extracts:\n" + "\n".join(lines)
    return text[:max_chars]
