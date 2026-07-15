"""Module contract: lifecycle, config hooks, I/O; write-back reserved."""

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


@dataclass
class ModuleOutput:
    """Structured result a module can return to the shell."""

    summary: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class Module(ABC):
    """Stable contract for life-domain modules."""

    meta: ModuleMeta

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

    def write_back(self, payload: dict[str, Any]) -> ModuleOutput:
        """Reserved for later. Must not be used in Sprint 1."""
        raise NotImplementedError(
            f"write-back is reserved; not enabled for {self.meta.id}"
        )
