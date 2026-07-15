"""Fitness lite — goal prompt → non-clinical LLM plan."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from crawley.data.paths import FITNESS_DIR, ensure_data_dirs
from crawley.jobs import JobState
from crawley.llm.base import ChatMessage, LLMError
from crawley.llm.factory import get_llm_provider
from crawley.modules.contract import Module, ModuleKind, ModuleMeta, ModuleOutput
from crawley.prompts import build_fitness_user_message
from crawley.settings import load_settings

logger = logging.getLogger(__name__)

DEFAULT_GOAL = "Build a sustainable weekday movement habit (walks + light strength)."
LAST_GOAL_PATH = FITNESS_DIR / "last_goal.txt"


def load_last_goal() -> str:
    ensure_data_dirs()
    if LAST_GOAL_PATH.exists():
        text = LAST_GOAL_PATH.read_text(encoding="utf-8").strip()
        if text:
            return text
    return DEFAULT_GOAL


def save_last_goal(goal: str) -> None:
    ensure_data_dirs()
    LAST_GOAL_PATH.write_text(goal.strip() + "\n", encoding="utf-8")


class FitnessModule(Module):
    meta = ModuleMeta(
        id="fitness",
        title="Fitness",
        kind=ModuleKind.LIVE,
        nav_order=40,
        description="Personal goals and starter plan breakdown (not medical advice).",
    )

    def __init__(self) -> None:
        self.job = JobState(
            status="idle",
            message="Enter a short goal, then run for an introductory plan.",
        )
        self._executor = None

    def bind_executor(self, executor) -> None:
        self._executor = executor

    def panel_context(self) -> dict[str, Any]:
        return {
            "coming_soon": False,
            "description": self.meta.description,
            "job": self.job.to_dict(),
            "default_goal": load_last_goal(),
            "disclaimer": (
                "Not medical advice. Personal planning only — talk to a qualified "
                "professional before changing exercise or health routines."
            ),
        }

    def run(self, inputs: dict[str, Any] | None = None) -> ModuleOutput:
        inputs = inputs or {}
        goal = (inputs.get("goal") or load_last_goal()).strip()
        if not goal:
            return ModuleOutput(error="A short goal is required.")
        if self.job.status == "busy":
            return ModuleOutput(error="Fitness job already running.")
        if self._executor is None:
            return ModuleOutput(error="Executor not configured.")

        save_last_goal(goal)
        self.job = JobState(status="busy", message="Drafting plan…")
        self._executor.submit(self._job_body, goal)
        return ModuleOutput(summary="started", details={"status": "busy"})

    def _job_body(self, goal: str) -> None:
        try:
            self.job = JobState(status="busy", message="Calling LLM…")
            prompts = load_settings().prompts
            system = prompts.fitness_system
            user = build_fitness_user_message(
                header=prompts.fitness_user_header,
                goal=goal,
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
                message="Done — introductory plan ready.",
                summary=result.content,
                details={
                    "goal": goal,
                    "model": result.model,
                    "prompt_system": system,
                    "prompt_user": user,
                },
            )
            try:
                from crawley.data.snapshots import save_snapshot

                save_snapshot("fitness", result.content)
            except Exception:  # noqa: BLE001
                logger.exception("Failed to persist fitness snapshot")
        except LLMError as exc:
            self.job = JobState(status="error", message=str(exc))
        except Exception as exc:  # noqa: BLE001
            logger.exception("Fitness job failed")
            self.job = JobState(status="error", message=f"Fitness run failed: {exc}")


def last_goal_path() -> Path:
    return LAST_GOAL_PATH
