"""Co-parenting schedule lite — local windows → LLM skim."""

from __future__ import annotations

import json
import logging
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from crawley.data.paths import CO_PARENTING_DIR, ensure_data_dirs
from crawley.jobs import JobState
from crawley.llm.base import ChatMessage, LLMError
from crawley.llm.factory import get_llm_provider
from crawley.modules.contract import Module, ModuleKind, ModuleMeta, ModuleOutput
from crawley.prompts import build_co_parenting_user_message
from crawley.settings import load_settings

logger = logging.getLogger(__name__)

SCHEDULE_PATH = CO_PARENTING_DIR / "schedule.json"
LOOKAHEAD_DAYS = 14


def _default_schedule() -> list[dict[str, str]]:
    today = date.today()
    return [
        {
            "date": (today + timedelta(days=2)).isoformat(),
            "window": "Fri 15:00–Sun 18:00",
            "notes": "Handoff at school",
        },
        {
            "date": (today + timedelta(days=9)).isoformat(),
            "window": "Fri 15:00–Sun 18:00",
            "notes": "Weekend with kids",
        },
    ]


def load_schedule() -> list[dict[str, str]]:
    ensure_data_dirs()
    if SCHEDULE_PATH.exists():
        try:
            raw = json.loads(SCHEDULE_PATH.read_text(encoding="utf-8"))
            if isinstance(raw, list) and raw:
                return [
                    {
                        "date": str(item.get("date") or "").strip(),
                        "window": str(item.get("window") or "").strip(),
                        "notes": str(item.get("notes") or "").strip(),
                    }
                    for item in raw
                    if isinstance(item, dict)
                ]
        except (OSError, json.JSONDecodeError):
            logger.exception("Failed to load co-parenting schedule")
    return _default_schedule()


def save_schedule(entries: list[dict[str, str]]) -> None:
    ensure_data_dirs()
    CO_PARENTING_DIR.mkdir(parents=True, exist_ok=True)
    SCHEDULE_PATH.write_text(
        json.dumps(entries, indent=2) + "\n",
        encoding="utf-8",
    )


def schedule_as_text(entries: list[dict[str, str]]) -> str:
    lines = []
    for item in entries:
        lines.append(
            f"- {item.get('date', '')}: {item.get('window', '')}"
            + (f" — {item['notes']}" if item.get("notes") else "")
        )
    return "\n".join(lines)


def parse_schedule_text(text: str) -> list[dict[str, str]]:
    """Parse simple lines: YYYY-MM-DD | window | notes"""
    entries: list[dict[str, str]] = []
    for line in text.splitlines():
        line = line.strip().lstrip("-").strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) == 1 and ":" in line:
            # Allow "YYYY-MM-DD: window — notes"
            date_part, rest = line.split(":", 1)
            window = rest
            notes = ""
            if "—" in rest:
                window, notes = rest.split("—", 1)
            entries.append(
                {
                    "date": date_part.strip(),
                    "window": window.strip(),
                    "notes": notes.strip(),
                }
            )
            continue
        if len(parts) >= 2:
            entries.append(
                {
                    "date": parts[0],
                    "window": parts[1],
                    "notes": parts[2] if len(parts) > 2 else "",
                }
            )
    return entries


class CoParentingModule(Module):
    meta = ModuleMeta(
        id="co-parenting",
        title="Co-parenting",
        kind=ModuleKind.LIVE,
        nav_order=50,
        description="Local handoff schedule skim (sole operator; no shared accounts).",
    )

    def __init__(self) -> None:
        self.job = JobState(
            status="idle",
            message="Edit the schedule, Save, then Run for what’s next.",
        )
        self._executor = None

    def bind_executor(self, executor) -> None:
        self._executor = executor

    def panel_context(self) -> dict[str, Any]:
        entries = load_schedule()
        return {
            "coming_soon": False,
            "description": self.meta.description,
            "job": self.job.to_dict(),
            "notes": schedule_as_text(entries),
            "notes_path": str(SCHEDULE_PATH),
            "lookahead_days": LOOKAHEAD_DAYS,
            "format_hint": (
                "One line per entry: YYYY-MM-DD | window | notes "
                "(or YYYY-MM-DD: window — notes)"
            ),
        }

    def save_only(self, notes: str) -> ModuleOutput:
        text = notes.strip()
        if not text:
            return ModuleOutput(error="Schedule cannot be empty.")
        entries = parse_schedule_text(text)
        if not entries:
            return ModuleOutput(
                error="Could not parse schedule lines. Use date | window | notes."
            )
        save_schedule(entries)
        self.job = JobState(
            status="idle",
            message="Schedule saved locally. Run when ready.",
        )
        return ModuleOutput(summary="saved", details={"count": len(entries)})

    def run(self, inputs: dict[str, Any] | None = None) -> ModuleOutput:
        inputs = inputs or {}
        notes = (inputs.get("notes") or schedule_as_text(load_schedule())).strip()
        if not notes:
            return ModuleOutput(error="Schedule is required.")
        if self.job.status == "busy":
            return ModuleOutput(error="Co-parenting job already running.")
        if self._executor is None:
            return ModuleOutput(error="Executor not configured.")

        entries = parse_schedule_text(notes)
        if not entries:
            return ModuleOutput(error="Could not parse schedule lines.")
        save_schedule(entries)
        self.job = JobState(status="busy", message="Skimming schedule…")
        self._executor.submit(self._job_body, entries)
        return ModuleOutput(summary="started", details={"status": "busy"})

    def _job_body(self, entries: list[dict[str, str]]) -> None:
        try:
            today = date.today()
            end = today + timedelta(days=LOOKAHEAD_DAYS)
            bounded = []
            for item in entries:
                try:
                    d = date.fromisoformat(item["date"])
                except ValueError:
                    bounded.append(item)
                    continue
                if today <= d <= end:
                    bounded.append(item)
            if not bounded:
                empty = (
                    f"## Quiet window\n\n"
                    f"No schedule entries in the next {LOOKAHEAD_DAYS} days.\n"
                )
                self.job = JobState(
                    status="done",
                    message="No entries in the bounded window.",
                    summary=empty,
                )
                try:
                    from crawley.data.snapshots import save_snapshot

                    save_snapshot("co-parenting", empty)
                except Exception:  # noqa: BLE001
                    logger.exception("Failed to persist empty co-parenting snapshot")
                return

            self.job = JobState(status="busy", message="Calling LLM…")
            prompts = load_settings().prompts
            system = prompts.co_parenting_system
            user = build_co_parenting_user_message(
                header=prompts.co_parenting_user_header,
                schedule_lines=[
                    f"- {e['date']}: {e['window']}"
                    + (f" — {e['notes']}" if e.get("notes") else "")
                    for e in bounded
                ],
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
                message=f"Done — {len(bounded)} entries in window.",
                summary=result.content,
                details={
                    "count": len(bounded),
                    "model": result.model,
                    "prompt_system": system,
                    "prompt_user": user,
                },
            )
            try:
                from crawley.data.snapshots import save_snapshot

                save_snapshot("co-parenting", result.content)
            except Exception:  # noqa: BLE001
                logger.exception("Failed to persist co-parenting snapshot")
        except LLMError as exc:
            self.job = JobState(status="error", message=str(exc))
        except Exception as exc:  # noqa: BLE001
            logger.exception("Co-parenting job failed")
            self.job = JobState(
                status="error",
                message=f"Co-parenting run failed: {exc}",
            )


def schedule_path() -> Path:
    return SCHEDULE_PATH
