"""Explicit in-repo module registry."""

from __future__ import annotations

from crawley.modules.calendar import CalendarModule
from crawley.modules.coding_creative import CodingCreativeModule
from crawley.modules.co_parenting import CoParentingModule
from crawley.modules.contract import Module
from crawley.modules.diy import DiyModule
from crawley.modules.finance import FinanceModule
from crawley.modules.fitness import FitnessModule
from crawley.modules.gmail import GmailModule
from crawley.modules.investment import InvestmentModule
from crawley.modules.work import WorkModule


def build_registry() -> dict[str, Module]:
    """Return modules keyed by id."""
    modules: list[Module] = [
        InvestmentModule(),
        GmailModule(),
        CalendarModule(),
        FitnessModule(),
        CoParentingModule(),
        DiyModule(),
        WorkModule(),
        FinanceModule(),
        CodingCreativeModule(),
    ]
    return {m.meta.id: m for m in modules}


def nav_modules(registry: dict[str, Module]) -> list[Module]:
    return sorted(registry.values(), key=lambda m: (m.meta.nav_order, m.meta.title))
