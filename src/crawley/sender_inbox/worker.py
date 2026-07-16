"""Background one-at-a-time email ingest worker."""

from __future__ import annotations

import logging
import os
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
    reset_poc_data,
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


def external_worker_mode() -> bool:
    """True when ingest loop is owned by `crawley.daemons.gmail_ingest`."""
    raw = os.environ.get("CRAWLEY_GMAIL_WORKER", "").strip().lower()
    return raw in {"daemon", "external", "1", "true", "yes"}


def is_running() -> bool:
    return _running


def request_pause() -> None:
    state = load_ingest_state()
    state["pause_requested"] = True
    if state.get("status") in {"busy", "queued"}:
        state["current_line"] = "Pause / stop requested…"
    save_ingest_state(state)


def _prepare_ingest_state(*, force: bool) -> tuple[bool, str, dict[str, Any] | None]:
    """Validate and prepare ingest_state. Does not set _running."""
    state = load_ingest_state()
    if state.get("status") == "busy":
        return False, "Ingest already running.", None
    creds = load_credentials()
    if not creds:
        return False, "Google token missing or invalid. Connect Google first.", None
    # Reset only after auth checks so a failed Start does not wipe data.
    if force:
        reset_poc_data()
        state = load_ingest_state()
    if remaining_capacity() <= 0:
        state["status"] = "done"
        state["current_line"] = f"PoC cap reached ({state.get('cap') or POC_CAP})."
        save_ingest_state(state)
        return False, state["current_line"], None
    state["pause_requested"] = False
    state["last_error"] = ""
    state["force_requested"] = bool(force)
    state["cap"] = int(state.get("cap") or POC_CAP)
    return True, "ok", state


def queue_ingest_for_daemon(*, force: bool = False) -> tuple[bool, str]:
    """API path when CRAWLEY_GMAIL_WORKER=daemon — hand off via ingest_state.json."""
    with _worker_lock:
        state = load_ingest_state()
        if state.get("status") == "busy":
            return False, "Ingest already running."
        if state.get("start_requested") or state.get("status") == "queued":
            return False, "Ingest already queued for gmail-ingest daemon."
        ok, msg, prepared = _prepare_ingest_state(force=force)
        if not ok or prepared is None:
            return False, msg
        prepared["start_requested"] = True
        prepared["status"] = "queued"
        prepared["current_line"] = "Queued for gmail-ingest daemon…"
        save_ingest_state(prepared)
    return True, "Ingest queued for gmail-ingest daemon."


def start_ingest(executor, *, force: bool = False) -> tuple[bool, str]:
    """Start ingest in-process (default) or queue for external daemon."""
    global _running
    if external_worker_mode():
        return queue_ingest_for_daemon(force=force)
    with _worker_lock:
        if _running:
            return False, "Ingest already running."
        state = load_ingest_state()
        if state.get("start_requested") or state.get("status") == "queued":
            return False, "Ingest already queued for gmail-ingest daemon."
        ok, msg, prepared = _prepare_ingest_state(force=force)
        if not ok or prepared is None:
            return False, msg
        _running = True
        prepared["start_requested"] = False
        prepared["status"] = "busy"
        prepared["current_line"] = "Starting ingest…"
        save_ingest_state(prepared)
    # Submit outside the lock — sync executors in tests must not deadlock on finally.
    executor.submit(_worker_body)
    return True, "Ingest started."


def run_ingest_in_this_process(*, force: bool = False) -> tuple[bool, str]:
    """Daemon entrypoint: claim work and run `_worker_body` on this thread."""
    global _running
    with _worker_lock:
        if _running:
            return False, "Ingest already running in this process."
        state = load_ingest_state()
        if state.get("start_requested") or state.get("status") == "queued":
            force = force or bool(state.get("force_requested"))
            state["start_requested"] = False
            if state.get("status") == "queued":
                state["status"] = "idle"
            save_ingest_state(state)
        ok, msg, prepared = _prepare_ingest_state(force=force)
        if not ok or prepared is None:
            return False, msg
        _running = True
        prepared["start_requested"] = False
        prepared["force_requested"] = False
        prepared["status"] = "busy"
        prepared["pause_requested"] = False
        prepared["current_line"] = "Starting ingest (daemon)…"
        save_ingest_state(prepared)
    _worker_body()
    return True, "Ingest finished."


def claim_queued_ingest() -> bool:
    """Return True if a daemon should run (start_requested set)."""
    state = load_ingest_state()
    return bool(state.get("start_requested")) or state.get("status") == "queued"


def stop_ingest() -> tuple[bool, str]:
    """Request pause / stop (in-process or daemon); cancel queued starts."""
    state = load_ingest_state()
    if is_running() or state.get("status") in {"busy", "queued"} or state.get("start_requested"):
        if state.get("status") == "queued" or state.get("start_requested"):
            state["start_requested"] = False
            state["status"] = "idle"
            state["current_line"] = "Queued ingest cancelled."
            state["pause_requested"] = False
            save_ingest_state(state)
            return True, "Queued ingest cancelled."
        request_pause()
        return True, "Stop requested."
    return False, "Ingest is not running."


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
