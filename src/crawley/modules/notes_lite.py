"""Shared notes → LLM Markdown pattern for lite life modules."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Callable

from crawley.data.paths import ensure_data_dirs
from crawley.jobs import JobState
from crawley.llm.base import ChatMessage, LLMError
from crawley.llm.factory import get_llm_provider
from crawley.modules.contract import Module, ModuleMeta, ModuleOutput
from crawley.settings import load_settings

logger = logging.getLogger(__name__)


class NotesLiteModule(Module):
    """
    Local notes file + Save / Run LLM Markdown + home snapshot.

    Subclasses set ``meta``, paths, default notes, prompt attribute names,
    and optional disclaimer / empty-run message.
    """

    meta: ModuleMeta
    notes_dir: Path
    notes_filename: str = "notes.txt"
    default_notes: str = ""
    system_attr: str = ""
    header_attr: str = ""
    busy_message: str = "Summarizing…"
    done_message: str = "Done — summary ready."
    max_tokens: int = 500
    disclaimer: str | None = None
    user_builder: Callable[[str, str], str] | None = None

    def __init__(self) -> None:
        self.job = JobState(
            status="idle",
            message="Edit notes, Save, then Run.",
        )
        self._executor = None

    @property
    def notes_path(self) -> Path:
        return self.notes_dir / self.notes_filename

    def bind_executor(self, executor) -> None:
        self._executor = executor

    def load_notes(self) -> str:
        ensure_data_dirs()
        path = self.notes_path
        if path.exists():
            text = path.read_text(encoding="utf-8").strip()
            if text:
                return text
        return self.default_notes

    def save_notes(self, notes: str) -> None:
        ensure_data_dirs()
        self.notes_dir.mkdir(parents=True, exist_ok=True)
        self.notes_path.write_text(notes.strip() + "\n", encoding="utf-8")

    def panel_context(self) -> dict[str, Any]:
        ctx: dict[str, Any] = {
            "coming_soon": False,
            "description": self.meta.description,
            "job": self.job.to_dict(),
            "notes": self.load_notes(),
            "notes_path": str(self.notes_path),
        }
        if self.disclaimer:
            ctx["disclaimer"] = self.disclaimer
        return ctx

    def save_only(self, notes: str) -> ModuleOutput:
        text = notes.strip()
        if not text:
            return ModuleOutput(error="Notes cannot be empty.")
        self.save_notes(text)
        self.job = JobState(
            status="idle",
            message="Notes saved locally. Run when ready.",
        )
        return ModuleOutput(summary="saved", details={"path": str(self.notes_path)})

    def run(self, inputs: dict[str, Any] | None = None) -> ModuleOutput:
        inputs = inputs or {}
        notes = (inputs.get("notes") or self.load_notes()).strip()
        if not notes:
            return ModuleOutput(error="Notes are required.")
        if self.job.status == "busy":
            return ModuleOutput(error=f"{self.meta.title} job already running.")
        if self._executor is None:
            return ModuleOutput(error="Executor not configured.")

        self.save_notes(notes)
        self.job = JobState(status="busy", message=self.busy_message)
        self._executor.submit(self._job_body, notes)
        return ModuleOutput(summary="started", details={"status": "busy"})

    def _build_user(self, header: str, notes: str) -> str:
        if self.user_builder is not None:
            return self.user_builder(header, notes)
        return f"{header.rstrip()}\n{notes.strip()}\n"

    def _job_body(self, notes: str) -> None:
        try:
            self.job = JobState(status="busy", message="Calling LLM…")
            prompts = load_settings().prompts
            system = getattr(prompts, self.system_attr)
            header = getattr(prompts, self.header_attr)
            user = self._build_user(header, notes)
            # Optional shared-context injection for modules that opt in via inputs later.
            provider = get_llm_provider()
            result = provider.complete(
                [
                    ChatMessage(role="system", content=system),
                    ChatMessage(role="user", content=user),
                ],
                max_tokens=self.max_tokens,
            )
            self.job = JobState(
                status="done",
                message=self.done_message,
                summary=result.content,
                details={
                    "model": result.model,
                    "prompt_system": system,
                    "prompt_user": user,
                },
            )
            try:
                from crawley.data.snapshots import save_snapshot

                save_snapshot(self.meta.id, result.content)
            except Exception:  # noqa: BLE001
                logger.exception("Failed to persist %s snapshot", self.meta.id)
        except LLMError as exc:
            self.job = JobState(status="error", message=str(exc))
        except Exception as exc:  # noqa: BLE001
            logger.exception("%s job failed", self.meta.title)
            self.job = JobState(
                status="error",
                message=f"{self.meta.title} run failed: {exc}",
            )
