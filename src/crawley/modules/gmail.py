"""Gmail read-only bounded inbox skim (shared Google OAuth)."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from email.utils import parseaddr
from typing import Any

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from crawley.data.duck import duck_connection
from crawley.data.paths import GMAIL_DIR, ensure_data_dirs
from crawley.google_oauth import (
    TOKEN_PATH,
    authorization_url,
    finish_oauth,
    google_auth_status,
    load_credentials,
)
from crawley.jobs import JobState
from crawley.llm.base import ChatMessage, LLMError
from crawley.llm.factory import get_llm_provider
from crawley.modules.contract import Module, ModuleKind, ModuleMeta, ModuleOutput, WriteBackCapability
from crawley.prompts import build_gmail_user_message
from crawley.settings import load_settings

logger = logging.getLogger(__name__)

MAX_MESSAGES = 8

# Re-exported for routes / tests that historically imported from this module.
__all__ = [
    "GmailModule",
    "MAX_MESSAGES",
    "TOKEN_PATH",
    "authorization_url",
    "fetch_inbox_skim",
    "finish_oauth",
    "load_credentials",
]


def _header_map(payload_headers: list[dict[str, str]]) -> dict[str, str]:
    return {h.get("name", "").lower(): h.get("value", "") for h in payload_headers}


def _format_http_error(exc: HttpError) -> str:
    status = getattr(exc.resp, "status", None)
    reason = exc.reason or str(exc)
    if status in {401, 403}:
        return (
            f"Gmail auth failed ({status}): {reason}. "
            "Token may be expired or missing scope — reconnect Google (read-only)."
        )
    if status == 429:
        return (
            f"Gmail API quota exceeded ({status}): {reason}. "
            "Wait a bit, then retry a bounded skim."
        )
    return f"Gmail API error ({status or '?'}): {reason}"


def fetch_inbox_skim(creds, *, limit: int = MAX_MESSAGES) -> list[dict[str, str]]:
    service = build("gmail", "v1", credentials=creds, cache_discovery=False)
    listed = (
        service.users()
        .messages()
        .list(userId="me", labelIds=["INBOX"], maxResults=limit)
        .execute()
    )
    messages = listed.get("messages", [])
    rows: list[dict[str, str]] = []
    now = datetime.now(UTC).replace(tzinfo=None)
    ensure_data_dirs()
    cache_dir = GMAIL_DIR / datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    cache_dir.mkdir(parents=True, exist_ok=True)

    with duck_connection() as con:
        for meta in messages:
            msg_id = meta["id"]
            full = (
                service.users()
                .messages()
                .get(
                    userId="me",
                    id=msg_id,
                    format="metadata",
                    metadataHeaders=["From", "Subject", "Date"],
                )
                .execute()
            )
            headers = _header_map(full.get("payload", {}).get("headers", []))
            subject = headers.get("subject", "(no subject)")
            from_addr = parseaddr(headers.get("from", ""))[1] or headers.get("from", "")
            snippet = full.get("snippet", "")
            internal_ms = int(full.get("internalDate", "0"))
            internal_dt = (
                datetime.fromtimestamp(internal_ms / 1000, tz=UTC).replace(tzinfo=None)
                if internal_ms
                else now
            )
            (cache_dir / f"{msg_id}.txt").write_text(
                f"From: {from_addr}\nSubject: {subject}\n\n{snippet}\n",
                encoding="utf-8",
            )
            con.execute(
                """
                INSERT OR REPLACE INTO gmail_messages
                (id, fetched_at, internal_date, subject, from_addr, snippet)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                [msg_id, now, internal_dt, subject, from_addr, snippet[:500]],
            )
            rows.append(
                {
                    "id": msg_id,
                    "subject": subject,
                    "from": from_addr,
                    "snippet": snippet[:400],
                }
            )
    return rows


class GmailModule(Module):
    meta = ModuleMeta(
        id="gmail",
        title="Gmail",
        kind=ModuleKind.LIVE,
        nav_order=20,
        description="Sender Inbox — people-first ingest, profiles, and todos (PoC).",
    )
    write_back_capability = WriteBackCapability(
        supported=True,
        dry_run_only=True,
        label="Future: draft reply / label changes (not implemented)",
    )

    def __init__(self) -> None:
        self.job = JobState(
            status="idle",
            message="Connect Google (read-only), then run a bounded inbox skim.",
        )
        self._executor = None
        self.oauth_state: str | None = None

    def bind_executor(self, executor) -> None:
        self._executor = executor

    def auth_status(self) -> dict[str, Any]:
        status = google_auth_status()
        # Panel treats "connected" as ready-to-run when Gmail scope is present.
        return {
            **status,
            "connected": bool(status["connected"] and status["gmail_ok"]),
        }

    def panel_context(self) -> dict[str, Any]:
        from crawley.sender_inbox.formatters import relative_time
        from crawley.sender_inbox.schema import POC_CAP
        from crawley.sender_inbox.store import group_senders, progress_view
        from crawley.sender_inbox.worker import is_running

        progress = progress_view(running=is_running())
        senders = group_senders()
        for row in senders:
            row["latest_rel"] = relative_time(row.get("latest_at"))
        return {
            "coming_soon": False,
            "description": self.meta.description,
            "job": self.job.to_dict(),
            "auth": self.auth_status(),
            "max_messages": MAX_MESSAGES,
            "inbox_view": "list",
            "inbox_progress": progress,
            "inbox_senders": senders,
            "poc_cap": POC_CAP,
            "poll_inbox": progress.get("status") == "busy" or self.job.status == "busy",
        }

    def sender_panel_context(self, sender_id: str) -> dict[str, Any] | None:
        from crawley.sender_inbox.formatters import relative_time
        from crawley.sender_inbox.store import sender_detail

        detail = sender_detail(sender_id)
        if detail is None:
            return None
        for msg in detail["messages"]:
            msg["latest_rel"] = relative_time(msg.get("internal_date"))
            msg["signals"] = msg.get("signals") or []
        ctx = self.panel_context()
        ctx.update(
            {
                "inbox_view": "sender",
                "sender": detail,
                "poll_inbox": (detail.get("profile") or {}).get("status") == "generating"
                or ctx.get("poll_inbox"),
            }
        )
        return ctx

    def propose_write_back(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "module_id": "gmail",
            "action": payload.get("action") or "draft_reply",
            "payload": payload,
            "would_mutate": False,
            "api": "gmail.users.messages.send (not called)",
        }

    def run(self, inputs: dict[str, Any] | None = None) -> ModuleOutput:
        if self.job.status == "busy":
            return ModuleOutput(error="Gmail job already running.")
        if self._executor is None:
            return ModuleOutput(error="Executor not configured.")

        auth = self.auth_status()
        if not auth["client_ok"]:
            self.job = JobState(status="error", message=auth["error"] or "OAuth not configured.")
            return ModuleOutput(error=self.job.message)
        if not auth["connected"]:
            msg = auth.get("error") or "Gmail is not connected. Use Connect Google first."
            self.job = JobState(status="error", message=msg)
            return ModuleOutput(error=self.job.message)

        self.job = JobState(status="busy", message="Scanning inbox…")
        self._executor.submit(self._job_body)
        return ModuleOutput(summary="started", details={"status": "busy"})

    def _job_body(self) -> None:
        try:
            creds = load_credentials()
            if not creds:
                self.job = JobState(
                    status="error",
                    message="Google token missing or invalid. Reconnect Google.",
                )
                return
            self.job = JobState(status="busy", message="Fetching recent inbox messages…")
            rows = fetch_inbox_skim(creds)
            if not rows:
                empty = (
                    "## Empty inbox\n\n"
                    "No recent INBOX messages in this bounded skim.\n\n"
                    "### Priorities\n- None right now\n\n"
                    "### Follow-ups\n- None"
                )
                self.job = JobState(
                    status="done",
                    message="Inbox scan returned no messages.",
                    summary=empty,
                )
                try:
                    from crawley.data.snapshots import save_snapshot

                    save_snapshot("gmail", empty)
                except Exception:  # noqa: BLE001
                    logger.exception("Failed to persist empty gmail snapshot")
                return

            self.job = JobState(status="busy", message="Summarizing with LLM…")
            lines = [
                f"- From {r['from']}: {r['subject']} — {r['snippet'][:200]}" for r in rows
            ]
            prompts = load_settings().prompts
            system = prompts.gmail_system
            user = build_gmail_user_message(
                header=prompts.gmail_user_header,
                inbox_lines=lines,
            )
            provider = get_llm_provider()
            result = provider.complete(
                [
                    ChatMessage(role="system", content=system),
                    ChatMessage(role="user", content=user),
                ],
                max_tokens=450,
            )
            self.job = JobState(
                status="done",
                message=f"Done — skimmed {len(rows)} messages.",
                summary=result.content,
                details={
                    "count": len(rows),
                    "model": result.model,
                    "prompt_system": system,
                    "prompt_user": user,
                },
            )
            try:
                from crawley.data.snapshots import save_snapshot

                save_snapshot("gmail", result.content)
            except Exception:  # noqa: BLE001
                logger.exception("Failed to persist gmail snapshot")
        except HttpError as exc:
            self.job = JobState(status="error", message=_format_http_error(exc))
        except LLMError as exc:
            self.job = JobState(status="error", message=str(exc))
        except Exception as exc:  # noqa: BLE001
            logger.exception("Gmail job failed")
            self.job = JobState(status="error", message=f"Gmail run failed: {exc}")
