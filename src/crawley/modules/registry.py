"""Product module registry — emptied in Sprint 35 cutover.

Calendar and lite life modules live under ``crawley._quarantine`` and are
**not** imported here. ASX desk + Sender Inbox brains are
``crawley.asx_desk`` / ``crawley.sender_inbox`` (JSON API), not HTMX modules.
"""

from __future__ import annotations

from crawley.modules.contract import Module


def build_registry() -> dict[str, Module]:
    """Return product modules keyed by id (empty after HTMX cutover)."""
    return {}


def nav_modules(registry: dict[str, Module]) -> list[Module]:
    return sorted(registry.values(), key=lambda m: (m.meta.nav_order, m.meta.title))
