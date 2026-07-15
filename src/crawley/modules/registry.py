"""Explicit in-repo module registry."""

from __future__ import annotations

from crawley.modules.calendar import CalendarModule
from crawley.modules.contract import Module, ModuleKind, ModuleMeta
from crawley.modules.fitness import FitnessModule
from crawley.modules.gmail import GmailModule
from crawley.modules.investment import InvestmentModule
from crawley.modules.stubs import make_stub
from crawley.modules.work import WorkModule


def build_registry() -> dict[str, Module]:
    """Return modules keyed by id."""
    modules: list[Module] = [
        InvestmentModule(),
        GmailModule(),
        CalendarModule(),
        FitnessModule(),
        make_stub(
            ModuleMeta(
                id="co-parenting",
                title="Co-parenting",
                kind=ModuleKind.STUB,
                nav_order=50,
                description="Co-parenting schedule comes later.",
            )
        ),
        make_stub(
            ModuleMeta(
                id="diy",
                title="DIY",
                kind=ModuleKind.STUB,
                nav_order=60,
                description="DIY project tracking comes later.",
            )
        ),
        WorkModule(),
        make_stub(
            ModuleMeta(
                id="finance-taxes",
                title="Finance/Taxes",
                kind=ModuleKind.STUB,
                nav_order=80,
                description="Personal finance depth comes later.",
            )
        ),
        make_stub(
            ModuleMeta(
                id="coding-creative",
                title="Coding/Creative",
                kind=ModuleKind.STUB,
                nav_order=90,
                description="Coding and creative projects come later.",
            )
        ),
    ]
    return {m.meta.id: m for m in modules}


def nav_modules(registry: dict[str, Module]) -> list[Module]:
    return sorted(registry.values(), key=lambda m: (m.meta.nav_order, m.meta.title))
