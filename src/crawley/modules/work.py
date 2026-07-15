"""Work lite — local tasks/notes → LLM prioritization."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from crawley.data.paths import WORK_DIR, ensure_data_dirs
from crawley.jobs import JobState
from crawley.llm.base import ChatMessage, LLMError
from crawley.llm.factory import get_llm_provider
from crawley.modules.contract import Module, ModuleKind, ModuleMeta, ModuleOutput
from crawley.prompts import build_work_user_message
from crawley.settings import load_settings

logger = logging.getLogger(__name__)

DEFAULT_NOTES = (
    "- Finish sprint review notes\n"
    "- Reply to two follow-ups\n"
    "- Block focus time for deep work"
)
NOTES_PATH = WORK_DIR / "notes.txt"


def load_notes() -> str:
    ensure_data_dirs()
    if NOTES_PATH.exists():
        text = NOTES_PATH.read_text(encoding="utf-8").strip()
        if text:
            return text
    return DEFAULT_NOTES


def save_notes(notes: str) -> None:
    ensure_data_dirs()
    NOTES_PATH.write_text(notes.strip() + "\n", encoding="utf-8")


class WorkModule(Module):
    meta = ModuleMeta(
        id="work",
        title="Work",
        kind=ModuleKind.LIVE,
        nav_order=70,
        description="Local tasks/notes with LLM prioritization (no suite OAuth).",
    )

    def __init__(self) -> None:
        self.job = JobState(
            status="idle",
            message="Edit this week’s notes, Save, then Prioritize.",
        )
        self._executor = None

    def bind_executor(self, executor) -> None:
        self._executor = executor

    def panel_context(self) -> dict[str, Any]:
        return {
            "coming_soon": False,
            "description": self.meta.description,
            "job": self.job.to_dict(),
            "notes": load_notes(),
            "notes_path": str(NOTES_PATH),
        }

    def run(self, inputs: dict[str, Any] | None = None) -> ModuleOutput:
        inputs = inputs or {}
        notes = (inputs.get("notes") or load_notes()).strip()
        if not notes:
            return ModuleOutput(error="Notes or a task list is required.")
        if self.job.status == "busy":
            return ModuleOutput(error="Work job already running.")
        if self._executor is None:
            return ModuleOutput(error="Executor not configured.")

        save_notes(notes)
        self.job = JobState(status="busy", message="Prioritizing…")
        self._executor.submit(self._job_body, notes)
        return ModuleOutput(summary="started", details={"status": "busy"})

    def save_only(self, notes: str) -> ModuleOutput:
        text = notes.strip()
        if not text:
            return ModuleOutput(error="Notes cannot be empty.")
        save_notes(text)
        self.job = JobState(
            status="idle",
            message="Notes saved locally. Run Prioritize when ready.",
        )
        return ModuleOutput(summary="saved", details={"path": str(NOTES_PATH)})

    def _job_body(self, notes: str) -> None:
        try:
            self.job = JobState(status="busy", message="Calling LLM…")
            prompts = load_settings().prompts
            system = prompts.work_system
            user = build_work_user_message(
                header=prompts.work_user_header,
                notes=notes,
            )
            provider = get_llm_provider()
            result = provider.complete(
                [
                    ChatMessage(role="system", content=system),
                    ChatMessage(role="user", content=user),
                ],
                max_tokens=500,
            )
            self.job = JobState(
                status="done",
                message="Done — prioritization ready.",
                summary=result.content,
                details={
                    "model": result.model,
                    "prompt_system": system,
                    "prompt_user": user,
                },
            )
            try:
                from crawley.data.snapshots import save_snapshot

                save_snapshot("work", result.content)
            except Exception:  # noqa: BLE001
                logger.exception("Failed to persist work snapshot")
        except LLMError as exc:
            self.job = JobState(status="error", message=str(exc))
        except Exception as exc:  # noqa: BLE001
            logger.exception("Work job failed")
            self.job = JobState(status="error", message=f"Work run failed: {exc}")


def notes_path() -> Path:
    return NOTES_PATH
