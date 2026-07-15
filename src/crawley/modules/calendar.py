"""Calendar read-only upcoming events + LLM summary."""

from __future__ import annotations

import logging
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

logger = logging.getLogger(__name__)

MAX_EVENTS = 12
LOOKAHEAD_DAYS = 7


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


class CalendarModule(Module):
    meta = ModuleMeta(
        id="calendar",
        title="Calendar",
        kind=ModuleKind.LIVE,
        nav_order=30,
        description="Read-only upcoming events skim and summary (lite PoC).",
    )
    write_back_capability = WriteBackCapability(
        supported=True,
        dry_run_only=True,
        label="Future: create event drafts (not implemented)",
    )

    def __init__(self) -> None:
        self.job = JobState(
            status="idle",
            message="Connect Google (read-only), then skim the next week of events.",
        )
        self._executor = None

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
        }

    def propose_write_back(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "module_id": "calendar",
            "action": payload.get("action") or "insert_event",
            "payload": payload,
            "would_mutate": False,
            "api": "calendar.events.insert (not called)",
        }

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
