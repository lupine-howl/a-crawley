"""Module contract: lifecycle, config hooks, I/O; write-back dry-run only."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ModuleKind(str, Enum):
    LIVE = "live"
    STUB = "stub"


@dataclass(frozen=True)
class ModuleMeta:
    id: str
    title: str
    kind: ModuleKind
    nav_order: int = 100
    description: str = ""


@dataclass(frozen=True)
class WriteBackCapability:
    """Per-module write-back flags (ADR-006). Live mutation stays off."""

    supported: bool = False
    dry_run_only: bool = True
    label: str = ""


@dataclass
class ModuleOutput:
    """Structured result a module can return to the shell."""

    summary: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class Module(ABC):
    """Stable contract for life-domain modules."""

    meta: ModuleMeta
    write_back_capability: WriteBackCapability = WriteBackCapability()

    def configure(self, config: dict[str, Any]) -> None:
        """Optional config / credential hooks. Default: no-op."""

    def startup(self) -> None:
        """Lifecycle: called when the app starts. Default: no-op."""

    def shutdown(self) -> None:
        """Lifecycle: called on shutdown. Default: no-op."""

    @abstractmethod
    def panel_context(self) -> dict[str, Any]:
        """Context for rendering this module's panel."""

    def run(self, inputs: dict[str, Any] | None = None) -> ModuleOutput:
        """Execute a read/analyze path. Stubs raise; live modules override."""
        raise NotImplementedError(f"{self.meta.id} does not implement run()")

    def propose_write_back(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Build a draft description for confirm UI / dry-run audit. Override when supported."""
        return {
            "module_id": self.meta.id,
            "action": "unspecified",
            "payload": payload,
            "would_mutate": False,
        }

    def write_back(self, payload: dict[str, Any]) -> ModuleOutput:
        """
        Write-back entrypoint (ADR-006).

        Default path records a **dry-run** when ``supported`` and ``dry_run_only``.
        Modules that ship live mutations (e.g. Calendar) override this method and
        set ``dry_run_only=False``. Never call Gmail send from the default path.
        """
        cap = self.write_back_capability
        if not cap.supported:
            return ModuleOutput(
                error=(
                    f"write-back is not enabled for {self.meta.id}. "
                    "See ADR-006 for the confirm → mutate design."
                )
            )
        if not cap.dry_run_only:
            return ModuleOutput(
                error=(
                    f"{self.meta.id} declared live write-back; override write_back() "
                    "on the module to implement confirm → execute."
                )
            )

        draft = self.propose_write_back(payload)
        from crawley.writeback import record_dry_run

        entry = record_dry_run(
            module_id=self.meta.id,
            stage="dry_run",
            draft=draft,
            note=cap.label or "dry-run only; no remote mutation",
        )
        return ModuleOutput(
            summary="Write-back dry-run recorded (no remote mutation).",
            details={"audit": entry, "draft": draft, "dry_run": True},
        )
