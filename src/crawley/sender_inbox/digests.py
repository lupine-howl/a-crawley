"""Thread digests for Sender Inbox (Sprint 22 / B44)."""

from __future__ import annotations

import json
import logging
import threading
from datetime import UTC, datetime
from typing import Any

from crawley.data.paths import ensure_data_dirs
from crawley.google_oauth import load_credentials
from crawley.llm.base import ChatMessage, LLMError
from crawley.llm.factory import get_llm_provider
from crawley.sender_inbox.fetch import fetch_thread_messages
from crawley.sender_inbox.store import inbox_dir

logger = logging.getLogger(__name__)

_lock = threading.RLock()
_job_lock = threading.Lock()
_running_thread: str | None = None

MAX_THREAD_MESSAGES = 12
MAX_BODY_CHARS = 3500
MAX_DIGEST_CHARS = 6000


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def digests_path():
    ensure_data_dirs()
    return inbox_dir() / "thread_digests.json"


def load_digests() -> dict[str, Any]:
    with _lock:
        path = digests_path()
        if not path.exists():
            return {}
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        return dict(raw) if isinstance(raw, dict) else {}


def save_digests(data: dict[str, Any]) -> None:
    with _lock:
        path = digests_path()
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        tmp.replace(path)


def get_digest(thread_id: str) -> dict[str, Any] | None:
    thread_id = (thread_id or "").strip()
    if not thread_id:
        return None
    return load_digests().get(thread_id)


def digests_for_sender(sender_id: str, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Recent threads for a sender with optional digest snapshot."""
    digests = load_digests()
    seen: dict[str, dict[str, Any]] = {}
    for msg in sorted(messages, key=lambda m: m.get("internal_date") or "", reverse=True):
        tid = (msg.get("thread_id") or "").strip()
        if not tid or tid in seen:
            continue
        row = digests.get(tid) or {
            "thread_id": tid,
            "status": "empty",
            "markdown": "",
            "error": "",
            "subject": msg.get("subject") or "",
            "message_count": 0,
            "updated_at": "",
        }
        seen[tid] = {
            **row,
            "subject": row.get("subject") or msg.get("subject") or "",
            "latest_at": msg.get("internal_date") or "",
            "sample_message_id": msg.get("id") or "",
        }
        if len(seen) >= 8:
            break
    return list(seen.values())


def _set_digest(thread_id: str, **fields: Any) -> dict[str, Any]:
    data = load_digests()
    row = dict(data.get(thread_id) or {"thread_id": thread_id})
    row.update(fields)
    row["thread_id"] = thread_id
    row["updated_at"] = _now_iso()
    data[thread_id] = row
    save_digests(data)
    return row


def generate_thread_digest_markdown(messages: list[dict[str, Any]]) -> str:
    lines = []
    for m in messages[:MAX_THREAD_MESSAGES]:
        body = (m.get("body_text") or m.get("snippet") or "")[:800]
        lines.append(
            f"From: {m.get('from_name') or ''} <{m.get('from_addr') or ''}>\n"
            f"Date: {m.get('internal_date') or ''}\n"
            f"Subject: {m.get('subject') or ''}\n"
            f"{body}\n"
        )
    system = (
        "Write a Markdown thread digest for a personal operator. "
        "Sections exactly: ## Summary, ## Asks, ## Commitments, ## Suggested next action. "
        "Suggested next action must be manual (no auto-send). "
        "Be honest when thin. Cite only what is in the thread."
    )
    user = "Thread messages (newest first, bounded):\n\n" + "\n---\n".join(lines)
    if len(user) > MAX_DIGEST_CHARS:
        user = user[: MAX_DIGEST_CHARS - 1] + "…"
    provider = get_llm_provider()
    result = provider.complete(
        [
            ChatMessage(role="system", content=system),
            ChatMessage(role="user", content=user),
        ],
        max_tokens=700,
    )
    return (result.content or "").strip()


def start_thread_digest(thread_id: str, executor, *, sender_id: str = "") -> tuple[bool, str]:
    """Schedule a bounded thread digest job."""
    global _running_thread
    thread_id = (thread_id or "").strip()
    if not thread_id:
        return False, "Thread id required."
    with _job_lock:
        if _running_thread:
            return False, f"Digest already running for thread {_running_thread}."
        creds = load_credentials()
        if not creds:
            return False, "Google token missing or invalid. Connect Google first."
        _running_thread = thread_id
        _set_digest(
            thread_id,
            status="busy",
            error="",
            markdown="",
            sender_id=sender_id,
        )

    def _body() -> None:
        global _running_thread
        try:
            creds_inner = load_credentials()
            if not creds_inner:
                raise RuntimeError("Google token missing.")
            messages = fetch_thread_messages(
                creds_inner,
                thread_id,
                max_messages=MAX_THREAD_MESSAGES,
                max_body_chars=MAX_BODY_CHARS,
            )
            if not messages:
                _set_digest(
                    thread_id,
                    status="error",
                    error="No messages found for this thread (bounded fetch).",
                    message_count=0,
                )
                return
            # Persist raw slice under data for inspection (hard-capped).
            art = inbox_dir() / "thread_artifacts"
            art.mkdir(parents=True, exist_ok=True)
            (art / f"{thread_id}.json").write_text(
                json.dumps(
                    {
                        "thread_id": thread_id,
                        "fetched_at": _now_iso(),
                        "messages": messages,
                    },
                    indent=2,
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            md = generate_thread_digest_markdown(messages)
            subject = messages[0].get("subject") or ""
            _set_digest(
                thread_id,
                status="done",
                markdown=md,
                error="",
                message_count=len(messages),
                subject=subject,
                sender_id=sender_id,
            )
        except (LLMError, RuntimeError, OSError, ValueError) as exc:
            logger.exception("Thread digest failed for %s", thread_id)
            _set_digest(thread_id, status="error", error=str(exc)[:400])
        except Exception as exc:  # noqa: BLE001
            logger.exception("Thread digest failed for %s", thread_id)
            _set_digest(thread_id, status="error", error=str(exc)[:400])
        finally:
            with _job_lock:
                if _running_thread == thread_id:
                    _running_thread = None

    executor.submit(_body)
    return True, "Thread digest started."


def is_digest_running(thread_id: str | None = None) -> bool:
    with _job_lock:
        if thread_id:
            return _running_thread == thread_id
        return _running_thread is not None
