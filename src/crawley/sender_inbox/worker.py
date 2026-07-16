"""Background one-at-a-time email ingest worker."""

from __future__ import annotations

import logging
import threading
from datetime import UTC, datetime
from typing import Any

from googleapiclient.errors import HttpError

from crawley.google_oauth import load_credentials
from crawley.llm.base import LLMError
from crawley.sender_inbox import fetch as inbox_fetch
from crawley.sender_inbox import llm_tasks
from crawley.sender_inbox.schema import POC_CAP, sender_id_for
from crawley.sender_inbox.store import (
    ingested_ids,
    load_ingest_state,
    load_messages,
    load_profiles,
    load_todos,
    remaining_capacity,
    save_ingest_state,
    save_profiles,
    save_todos,
    upsert_message,
)

logger = logging.getLogger(__name__)

_worker_lock = threading.Lock()
_running = False


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def is_running() -> bool:
    return _running


def request_pause() -> None:
    state = load_ingest_state()
    state["pause_requested"] = True
    if state.get("status") == "busy":
        state["current_line"] = "Pause requested — finishing current message if any…"
    save_ingest_state(state)


def start_ingest(executor) -> tuple[bool, str]:
    """Schedule worker on executor. Returns (ok, message)."""
    global _running
    with _worker_lock:
        if _running:
            return False, "Ingest already running."
        if remaining_capacity() <= 0:
            state = load_ingest_state()
            state["status"] = "done"
            state["current_line"] = f"PoC cap reached ({state.get('cap') or POC_CAP})."
            save_ingest_state(state)
            return False, state["current_line"]
        creds = load_credentials()
        if not creds:
            return False, "Google token missing or invalid. Connect Google first."
        _running = True
        state = load_ingest_state()
        state["status"] = "busy"
        state["pause_requested"] = False
        state["last_error"] = ""
        state["current_line"] = "Starting ingest…"
        state["cap"] = int(state.get("cap") or POC_CAP)
        save_ingest_state(state)
    # Submit outside the lock — sync executors in tests must not deadlock on finally.
    executor.submit(_worker_body)
    return True, "Ingest started."


def resume_ingest(executor) -> tuple[bool, str]:
    if is_running():
        return False, "Ingest already running."
    state = load_ingest_state()
    state["pause_requested"] = False
    save_ingest_state(state)
    return start_ingest(executor)


def _record_message_error(message_id: str, subject: str, error: str) -> None:
    state = load_ingest_state()
    errors = list(state.get("message_errors") or [])
    errors.append({"id": message_id, "subject": subject, "error": error[:300]})
    state["message_errors"] = errors[-20:]
    state["last_error"] = error[:300]
    save_ingest_state(state)


def _refresh_sender_artifacts(sender_id: str) -> None:
    messages = [m for m in load_messages() if m.get("sender_id") == sender_id]
    if not messages:
        return
    messages.sort(key=lambda m: m.get("internal_date") or "", reverse=True)
    head = messages[0]
    profiles = load_profiles()
    prior = profiles.get(sender_id) or {}
    profiles[sender_id] = {
        **prior,
        "status": "generating",
        "error": "",
        "updated_at": prior.get("updated_at") or "",
        "markdown": prior.get("markdown") or "",
    }
    save_profiles(profiles)
    try:
        markdown = llm_tasks.generate_sender_profile(
            {"from_name": head.get("from_name"), "from_addr": head.get("from_addr")},
            messages,
        )
        profiles = load_profiles()
        profiles[sender_id] = {
            "markdown": markdown,
            "status": "ready",
            "error": "",
            "updated_at": _now_iso(),
        }
        save_profiles(profiles)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Sender profile failed for %s", sender_id)
        profiles = load_profiles()
        prior = profiles.get(sender_id) or {}
        profiles[sender_id] = {
            **prior,
            "status": "error",
            "error": str(exc)[:300],
            "updated_at": prior.get("updated_at") or _now_iso(),
        }
        save_profiles(profiles)

    existing = [t for t in load_todos() if t.get("sender_id") == sender_id]
    others = [t for t in load_todos() if t.get("sender_id") != sender_id]
    try:
        merged = llm_tasks.extract_todos(sender_id, messages, existing)
        save_todos(others + merged)
    except Exception:  # noqa: BLE001
        logger.exception("Todo extract failed for %s", sender_id)


def regenerate_profile(sender_id: str, executor) -> tuple[bool, str]:
    messages = [m for m in load_messages() if m.get("sender_id") == sender_id]
    if not messages:
        return False, "No messages for sender."
    executor.submit(_refresh_sender_artifacts, sender_id)
    return True, "Updating profile…"


def _persist_glance_snapshot() -> None:
    try:
        from crawley.data.snapshots import save_snapshot
        from crawley.sender_inbox.store import group_senders, progress_view

        progress = progress_view()
        senders = group_senders()
        lines = [
            "## Sender Inbox",
            "",
            f"{progress['processed']} messages · {len(senders)} senders · cap {progress['cap']}",
            "",
        ]
        for row in senders[:8]:
            lines.append(
                f"- **{row['display_name']}** ({row['message_count']}) — "
                f"{', '.join(row['signals']) or 'quiet'}"
            )
        save_snapshot("gmail", "\n".join(lines))
    except Exception:  # noqa: BLE001
        logger.exception("Failed to persist Sender Inbox snapshot")


def _error_stub(message_id: str, subject: str, error: str, partial: dict[str, Any] | None) -> dict[str, Any]:
    base = {
        "id": message_id,
        "thread_id": "",
        "from_name": "",
        "from_addr": "error.local",
        "sender_id": sender_id_for(f"error:{message_id}"),
        "subject": subject,
        "snippet": "",
        "body_text": "",
        "internal_date": _now_iso(),
        "metrics": {},
        "error": error[:400],
        "ingested_at": _now_iso(),
    }
    if partial:
        base.update(
            {
                "thread_id": partial.get("thread_id") or "",
                "from_name": partial.get("from_name") or "",
                "from_addr": partial.get("from_addr") or base["from_addr"],
                "sender_id": partial.get("sender_id")
                or sender_id_for(partial.get("from_addr") or f"error:{message_id}"),
                "subject": partial.get("subject") or subject,
                "snippet": partial.get("snippet") or "",
                "body_text": partial.get("body_text") or "",
                "internal_date": partial.get("internal_date") or base["internal_date"],
            }
        )
    return base


def _worker_body() -> None:
    global _running
    try:
        while True:
            state = load_ingest_state()
            if state.get("pause_requested"):
                state["status"] = "paused"
                state["current_line"] = "Paused."
                save_ingest_state(state)
                return
            if remaining_capacity() <= 0:
                state = load_ingest_state()
                state["status"] = "done"
                state["pause_requested"] = False
                state["current_line"] = (
                    f"PoC cap reached ({state.get('cap') or POC_CAP}). "
                    "Reset PoC data to re-run."
                )
                save_ingest_state(state)
                _persist_glance_snapshot()
                return

            creds = load_credentials()
            if not creds:
                state = load_ingest_state()
                state["status"] = "error"
                state["last_error"] = "Google token missing."
                state["current_line"] = state["last_error"]
                save_ingest_state(state)
                return

            known = ingested_ids()
            try:
                candidates = inbox_fetch.list_candidate_ids(creds, max_results=50)
            except HttpError as exc:
                state = load_ingest_state()
                state["status"] = "error"
                state["last_error"] = f"Gmail list failed: {exc}"
                state["current_line"] = state["last_error"]
                save_ingest_state(state)
                return

            next_id = next((mid for mid in candidates if mid not in known), None)
            if not next_id:
                state = load_ingest_state()
                state["status"] = "done"
                state["current_line"] = (
                    f"No more INBOX candidates. Ingested {len(known)} / "
                    f"{state.get('cap') or POC_CAP}."
                )
                save_ingest_state(state)
                _persist_glance_snapshot()
                return

            state = load_ingest_state()
            state["status"] = "busy"
            state["current_line"] = "Fetching message…"
            save_ingest_state(state)

            subject = "(unknown)"
            partial: dict[str, Any] | None = None
            try:
                message = inbox_fetch.fetch_message(creds, next_id)
                partial = message
                subject = message.get("subject") or subject
                state = load_ingest_state()
                state["current_line"] = f"Categorizing: {subject[:80]}"
                save_ingest_state(state)
                metrics = llm_tasks.categorize_message(message)
                message["metrics"] = metrics
                message["error"] = None
                message["ingested_at"] = _now_iso()
                upsert_message(message)
                state = load_ingest_state()
                state["current_line"] = (
                    f"Ingested {state['processed']} / {state['cap']}: {subject[:80]}"
                )
                save_ingest_state(state)
                _refresh_sender_artifacts(message["sender_id"])
            except (HttpError, LLMError, ValueError) as exc:
                logger.warning("Isolated ingest failure for %s: %s", next_id, exc)
                stub = _error_stub(next_id, subject, str(exc), partial)
                upsert_message(stub)
                _record_message_error(next_id, stub.get("subject") or subject, str(exc))
                state = load_ingest_state()
                state["status"] = "busy"
                state["current_line"] = f"Skipped with error: {subject[:60]}"
                save_ingest_state(state)
            except Exception as exc:  # noqa: BLE001
                logger.exception("Hard ingest failure")
                state = load_ingest_state()
                state["status"] = "error"
                state["last_error"] = str(exc)[:400]
                state["current_line"] = state["last_error"]
                save_ingest_state(state)
                return
    finally:
        with _worker_lock:
            _running = False
