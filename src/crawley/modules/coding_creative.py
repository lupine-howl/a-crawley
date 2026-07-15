"""Coding/Creative lite — local project notes → LLM next experiments."""

from __future__ import annotations

import logging
from typing import Any

from crawley.data.paths import CODING_DIR
from crawley.data.snapshots import save_snapshot
from crawley.jobs import JobState
from crawley.llm.base import ChatMessage, LLMError
from crawley.llm.factory import get_llm_provider
from crawley.modules.contract import ModuleKind, ModuleMeta, ModuleOutput
from crawley.modules.notes_lite import NotesLiteModule
from crawley.settings import load_settings
from crawley.shared_context import append_context_to_user_message, build_shared_context

logger = logging.getLogger(__name__)

NOTES_DIR = CODING_DIR


class CodingCreativeModule(NotesLiteModule):
    meta = ModuleMeta(
        id="coding-creative",
        title="Coding/Creative",
        kind=ModuleKind.LIVE,
        nav_order=90,
        description="Local creative/coding notes with LLM next experiments (no forge OAuth).",
    )
    default_notes = (
        "# Side project focus\n"
        "- Finish README for personal tool\n"
        "- Sketch UI for weekend prototype\n"
        "- Try one small experiment tonight"
    )
    system_attr = "coding_system"
    header_attr = "coding_user_header"
    busy_message = "Prioritizing experiments…"
    done_message = "Done — next experiments ready."

    def __init__(self) -> None:
        self.notes_dir = NOTES_DIR
        self._include_shared = False
        super().__init__()

    def run(self, inputs: dict[str, Any] | None = None) -> ModuleOutput:
        inputs = inputs or {}
        self._include_shared = bool(inputs.get("include_shared_context"))
        return super().run(inputs)

    def _job_body(self, notes: str) -> None:
        try:
            self.job = JobState(status="busy", message="Calling LLM…")
            prompts = load_settings().prompts
            system = prompts.coding_system
            header = prompts.coding_user_header
            user = self._build_user(header, notes)
            if self._include_shared:
                bundle = build_shared_context()
                user = append_context_to_user_message(user, bundle)
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
                    "shared_context": self._include_shared,
                },
            )
            try:
                save_snapshot(self.meta.id, result.content)
            except Exception:  # noqa: BLE001
                logger.exception("Failed to persist coding-creative snapshot")
        except LLMError as exc:
            self.job = JobState(status="error", message=str(exc))
        except Exception as exc:  # noqa: BLE001
            logger.exception("Coding/Creative job failed")
            self.job = JobState(
                status="error",
                message=f"Coding/Creative run failed: {exc}",
            )
