"""Coming-soon stub modules."""

from __future__ import annotations

from typing import Any

from crawley.modules.contract import Module, ModuleKind, ModuleMeta, ModuleOutput


class StubModule(Module):
    def __init__(self, meta: ModuleMeta) -> None:
        if meta.kind is not ModuleKind.STUB:
            raise ValueError(f"StubModule requires kind=STUB, got {meta.kind}")
        self.meta = meta

    def panel_context(self) -> dict[str, Any]:
        return {
            "coming_soon": True,
            "message": "Coming soon",
            "description": self.meta.description,
        }

    def run(self, inputs: dict[str, Any] | None = None) -> ModuleOutput:
        return ModuleOutput(error="Coming soon — this module is not implemented yet.")


def make_stub(meta: ModuleMeta) -> StubModule:
    return StubModule(meta)
