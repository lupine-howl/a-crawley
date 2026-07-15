"""Calendar upcoming events + LLM summary + confirm-first event insert."""

from __future__ import annotations

import json
import logging
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from crawley.data.duck import duck_connection
from crawley.data.paths import CALENDAR_DIR, ensure_data_dirs
from crawley.google_oauth import google_auth_status, load_credentials
from crawley.jobs import JobState
from crawley.llm.base import ChatMessage, LLMError
from crawley.llm.factory import get_llm_provider
from crawley.modules.contract import (
    Module,
    ModuleKind,
    ModuleMeta,
    ModuleOutput,
    WriteBackCapability,
)
from crawley.prompts import build_calendar_user_message
from crawley.settings import load_settings
from crawley.writeback import read_audit_entries, record_audit

logger = logging.getLogger(__name__)

MAX_EVENTS = 12
LOOKAHEAD_DAYS = 7
DRAFTS_PATH = CALENDAR_DIR / "pending_drafts.json"


def _format_http_error(exc: HttpError) -> str:
    status = getattr(exc.resp, "status", None)
    reason = exc.reason or str(exc)
    if status in {401, 403}:
        return (
            f"Calendar auth failed ({status}): {reason}. "
            "Reconnect Google and ensure Calendar (read-only) is granted."
        )
    if status == 429:
        return f"Calendar API quota exceeded ({status}): {reason}. Retry later."
    return f"Calendar API error ({status or '?'}): {reason}"


def fetch_upcoming_events(
    creds,
    *,
    days: int = LOOKAHEAD_DAYS,
    limit: int = MAX_EVENTS,
) -> list[dict[str, str]]:
    service = build("calendar", "v3", credentials=creds, cache_discovery=False)
    now = datetime.now(UTC)
    time_min = now.isoformat().replace("+00:00", "Z")
    time_max = (now + timedelta(days=days)).isoformat().replace("+00:00", "Z")
    result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=time_min,
            timeMax=time_max,
            maxResults=limit,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    items = result.get("items", [])
    rows: list[dict[str, str]] = []
    ensure_data_dirs()
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    cache_dir = CALENDAR_DIR / stamp
    cache_dir.mkdir(parents=True, exist_ok=True)
    fetched_at = now.replace(tzinfo=None)

    with duck_connection() as con:
        for item in items:
            event_id = item.get("id") or ""
            summary = (item.get("summary") or "(no title)").strip()
            start = item.get("start") or {}
            end = item.get("end") or {}
            start_s = start.get("dateTime") or start.get("date") or ""
            end_s = end.get("dateTime") or end.get("date") or ""
            location = (item.get("location") or "").strip()
            description = (item.get("description") or "").strip()[:400]
            line = (
                f"title: {summary}\nstart: {start_s}\nend: {end_s}\n"
                f"location: {location}\n\n{description}\n"
            )
            (cache_dir / f"{event_id or len(rows)}.txt").write_text(line, encoding="utf-8")
            con.execute(
                """
                INSERT OR REPLACE INTO calendar_events
                (id, fetched_at, start_at, end_at, title, location, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    event_id or f"anon-{len(rows)}",
                    fetched_at,
                    start_s,
                    end_s,
                    summary,
                    location,
                    description,
                ],
            )
            rows.append(
                {
                    "id": event_id,
                    "title": summary,
                    "start": start_s,
                    "end": end_s,
                    "location": location,
                    "description": description,
                }
            )
    return rows


def _load_drafts() -> dict[str, dict[str, Any]]:
    ensure_data_dirs()
    if not DRAFTS_PATH.exists():
        return {}
    try:
        raw = json.loads(DRAFTS_PATH.read_text(encoding="utf-8"))
        return raw if isinstance(raw, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _save_drafts(drafts: dict[str, dict[str, Any]]) -> None:
    ensure_data_dirs()
    CALENDAR_DIR.mkdir(parents=True, exist_ok=True)
    DRAFTS_PATH.write_text(json.dumps(drafts, indent=2) + "\n", encoding="utf-8")


class CalendarModule(Module):
    meta = ModuleMeta(
        id="calendar",
        title="Calendar",
        kind=ModuleKind.LIVE,
        nav_order=30,
        description="Upcoming events skim; confirm-first event insert (ADR-006).",
    )
    write_back_capability = WriteBackCapability(
        supported=True,
        dry_run_only=False,
        label="Create calendar event (confirm required)",
    )

    def __init__(self) -> None:
        self.job = JobState(
            status="idle",
            message="Connect Google, skim the next week, or propose an event draft.",
        )
        self._executor = None
        self.pending_draft: dict[str, Any] | None = None

    def bind_executor(self, executor) -> None:
        self._executor = executor

    def auth_status(self) -> dict[str, Any]:
        status = google_auth_status()
        return {
            **status,
            "connected": bool(status["connected"] and status["calendar_ok"]),
        }

    def panel_context(self) -> dict[str, Any]:
        return {
            "coming_soon": False,
            "description": self.meta.description,
            "job": self.job.to_dict(),
            "auth": self.auth_status(),
            "max_events": MAX_EVENTS,
            "lookahead_days": LOOKAHEAD_DAYS,
            "pending_draft": self.pending_draft,
            "audit_entries": read_audit_entries(limit=12),
            "default_event": {
                "summary": "Crawley reminder",
                "start": (datetime.now(UTC) + timedelta(hours=2))
                .replace(minute=0, second=0, microsecond=0)
                .isoformat()
                .replace("+00:00", "Z"),
                "end": (datetime.now(UTC) + timedelta(hours=3))
                .replace(minute=0, second=0, microsecond=0)
                .isoformat()
                .replace("+00:00", "Z"),
                "description": "",
            },
        }

    def propose_write_back(self, payload: dict[str, Any]) -> dict[str, Any]:
        draft_id = str(uuid.uuid4())
        summary = (payload.get("summary") or "Untitled").strip() or "Untitled"
        start = (payload.get("start") or "").strip()
        end = (payload.get("end") or "").strip()
        description = (payload.get("description") or "").strip()
        draft = {
            "draft_id": draft_id,
            "module_id": "calendar",
            "action": "insert_event",
            "payload": {
                "summary": summary,
                "start": start,
                "end": end,
                "description": description,
                "calendar_id": "primary",
            },
            "would_mutate": True,
            "api": "calendar.events.insert",
        }
        drafts = _load_drafts()
        drafts[draft_id] = draft
        _save_drafts(drafts)
        self.pending_draft = draft
        record_audit(
            module_id="calendar",
            stage="propose",
            draft=draft,
            note="Draft stored pending confirm",
            dry_run=False,
            success=None,
        )
        return draft

    def cancel_write_back(self, draft_id: str) -> ModuleOutput:
        drafts = _load_drafts()
        draft = drafts.pop(draft_id, None)
        _save_drafts(drafts)
        if self.pending_draft and self.pending_draft.get("draft_id") == draft_id:
            self.pending_draft = None
        if draft is None:
            return ModuleOutput(error="Draft not found or already cleared.")
        record_audit(
            module_id="calendar",
            stage="cancel",
            draft=draft,
            note="Cancelled — no remote write",
            dry_run=False,
            success=True,
        )
        self.job = JobState(
            status="idle",
            message="Draft cancelled. No remote write.",
        )
        return ModuleOutput(summary="cancelled", details={"draft_id": draft_id})

    def write_back(self, payload: dict[str, Any]) -> ModuleOutput:
        """Confirm-first live insert, or dry-run when explicitly requested."""
        action = (payload.get("action") or "insert_event").strip()
        if action == "dry_run":
            draft = self.propose_write_back(payload)
            draft["would_mutate"] = False
            entry = record_audit(
                module_id="calendar",
                stage="dry_run",
                draft=draft,
                note="Explicit dry-run; no remote mutation",
                dry_run=True,
                success=True,
            )
            return ModuleOutput(
                summary="Write-back dry-run recorded (no remote mutation).",
                details={"audit": entry, "draft": draft, "dry_run": True},
            )

        if action == "propose":
            draft = self.propose_write_back(payload)
            self.job = JobState(
                status="idle",
                message="Draft ready — review and Confirm to insert, or Cancel.",
                details={"draft": draft},
            )
            return ModuleOutput(summary="proposed", details={"draft": draft})

        if action != "confirm":
            return ModuleOutput(error=f"Unknown write-back action: {action}")

        draft_id = (payload.get("draft_id") or "").strip()
        drafts = _load_drafts()
        draft = drafts.get(draft_id)
        if not draft:
            return ModuleOutput(error="Draft missing or expired. Propose again.")

        auth = self.auth_status()
        if not auth.get("calendar_write_ok"):
            msg = (
                "Calendar write scope missing. Reconnect Google with Calendar events "
                "write permission (Gmail send is not requested)."
            )
            record_audit(
                module_id="calendar",
                stage="execute",
                draft=draft,
                note=msg,
                dry_run=False,
                success=False,
            )
            return ModuleOutput(error=msg)

        try:
            creds = load_credentials()
            if not creds:
                return ModuleOutput(error="Google token missing. Reconnect Google.")
            body_payload = draft["payload"]
            body = {
                "summary": body_payload["summary"],
                "description": body_payload.get("description") or "",
                "start": {"dateTime": body_payload["start"], "timeZone": "UTC"},
                "end": {"dateTime": body_payload["end"], "timeZone": "UTC"},
            }
            service = build("calendar", "v3", credentials=creds, cache_discovery=False)
            created = (
                service.events()
                .insert(calendarId="primary", body=body)
                .execute()
            )
            drafts.pop(draft_id, None)
            _save_drafts(drafts)
            self.pending_draft = None
            result_draft = {
                **draft,
                "remote_event_id": created.get("id"),
                "html_link": created.get("htmlLink"),
            }
            entry = record_audit(
                module_id="calendar",
                stage="execute",
                draft=result_draft,
                note="Inserted into primary calendar",
                dry_run=False,
                success=True,
            )
            self.job = JobState(
                status="done",
                message=f"Event inserted: {body_payload['summary']}",
                summary=(
                    f"## Event created\n\n"
                    f"**{body_payload['summary']}**\n\n"
                    f"- Start: {body_payload['start']}\n"
                    f"- End: {body_payload['end']}\n"
                    + (
                        f"- [Open in Calendar]({created.get('htmlLink')})\n"
                        if created.get("htmlLink")
                        else ""
                    )
                ),
                details={"audit": entry, "event": created},
            )
            return ModuleOutput(
                summary="Event inserted.",
                details={"audit": entry, "event_id": created.get("id")},
            )
        except HttpError as exc:
            msg = _format_http_error(exc)
            record_audit(
                module_id="calendar",
                stage="execute",
                draft=draft,
                note=msg,
                dry_run=False,
                success=False,
            )
            return ModuleOutput(error=msg)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Calendar write-back failed")
            msg = f"Calendar insert failed: {exc}"
            record_audit(
                module_id="calendar",
                stage="execute",
                draft=draft,
                note=msg,
                dry_run=False,
                success=False,
            )
            return ModuleOutput(error=msg)

    def run(self, inputs: dict[str, Any] | None = None) -> ModuleOutput:
        if self.job.status == "busy":
            return ModuleOutput(error="Calendar job already running.")
        if self._executor is None:
            return ModuleOutput(error="Executor not configured.")

        auth = self.auth_status()
        if not auth["client_ok"]:
            self.job = JobState(status="error", message=auth["error"] or "OAuth not configured.")
            return ModuleOutput(error=self.job.message)
        if not auth["connected"]:
            msg = (
                auth.get("error")
                or "Calendar is not connected. Connect Google with Calendar read-only."
            )
            self.job = JobState(status="error", message=msg)
            return ModuleOutput(error=self.job.message)

        self.job = JobState(status="busy", message="Loading upcoming events…")
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
            self.job = JobState(status="busy", message="Fetching calendar events…")
            rows = fetch_upcoming_events(creds)
            if not rows:
                empty = (
                    f"## Empty calendar\n\n"
                    f"No events in the next {LOOKAHEAD_DAYS} days "
                    f"(bounded to {MAX_EVENTS}).\n"
                )
                self.job = JobState(
                    status="done",
                    message="No upcoming events in the bounded window.",
                    summary=empty,
                )
                try:
                    from crawley.data.snapshots import save_snapshot

                    save_snapshot("calendar", empty)
                except Exception:  # noqa: BLE001
                    logger.exception("Failed to persist empty calendar snapshot")
                return

            self.job = JobState(status="busy", message="Summarizing with LLM…")
            lines = [
                f"- {r['start']}: {r['title']}"
                + (f" @ {r['location']}" if r["location"] else "")
                + (f" — {r['description'][:120]}" if r["description"] else "")
                for r in rows
            ]
            prompts = load_settings().prompts
            system = prompts.calendar_system
            user = build_calendar_user_message(
                header=prompts.calendar_user_header,
                event_lines=lines,
            )
            provider = get_llm_provider()
            result = provider.complete(
                [
                    ChatMessage(role="system", content=system),
                    ChatMessage(role="user", content=user),
                ],
                max_tokens=400,
            )
            self.job = JobState(
                status="done",
                message=f"Done — {len(rows)} upcoming events.",
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

                save_snapshot("calendar", result.content)
            except Exception:  # noqa: BLE001
                logger.exception("Failed to persist calendar snapshot")
        except HttpError as exc:
            self.job = JobState(status="error", message=_format_http_error(exc))
        except LLMError as exc:
            self.job = JobState(status="error", message=str(exc))
        except Exception as exc:  # noqa: BLE001
            logger.exception("Calendar job failed")
            self.job = JobState(status="error", message=f"Calendar run failed: {exc}")
