"""Home Day brief — compose Calendar + Gmail snapshots (optional LLM refresh)."""

from __future__ import annotations

import logging
from typing import Any

from crawley.data.snapshots import get_snapshot, save_snapshot
from crawley.llm.base import ChatMessage, LLMError
from crawley.llm.factory import get_llm_provider
from crawley.settings import load_settings
from crawley.shared_context import append_context_to_user_message, build_shared_context

logger = logging.getLogger(__name__)

DAY_BRIEF_SNAPSHOT_ID = "day-brief"


def compose_day_brief_markdown(
    *,
    include_shared_context: bool = False,
) -> dict[str, Any]:
    """
    Build a Day brief from existing successful Calendar + Gmail snapshots.

    Does not invent content when a module never succeeded.
    """
    calendar = get_snapshot("calendar")
    gmail = get_snapshot("gmail")
    parts: list[str] = ["# Day brief"]
    sources: list[str] = []

    if calendar:
        parts.append("## Calendar\n" + calendar.summary_md.strip())
        sources.append("calendar")
    else:
        parts.append("## Calendar\n_No successful Calendar run yet._")

    if gmail:
        parts.append("## Inbox signals\n" + gmail.summary_md.strip())
        sources.append("gmail")
    else:
        parts.append("## Inbox signals\n_No successful Gmail run yet._")

    if not sources:
        md = (
            "# Day brief\n\n"
            "_Nothing to compose yet. Run Calendar and/or Gmail first._\n"
        )
        return {
            "markdown": md,
            "sources": [],
            "partial": True,
            "empty": True,
            "llm": False,
        }

    md = "\n\n".join(parts) + "\n"
    if include_shared_context:
        bundle = build_shared_context(module_ids=["work", "co-parenting", "fitness"])
        if bundle.text:
            md = md.rstrip() + "\n\n## Cross-cutting notes\n" + bundle.text + "\n"

    return {
        "markdown": md,
        "sources": sources,
        "partial": len(sources) < 2,
        "empty": False,
        "llm": False,
    }


def regenerate_day_brief_llm(
    *,
    include_shared_context: bool = False,
) -> dict[str, Any]:
    """Optional LLM compression of snapshot inputs into a short Day brief."""
    base = compose_day_brief_markdown(include_shared_context=False)
    if base["empty"]:
        return base

    calendar = get_snapshot("calendar")
    gmail = get_snapshot("gmail")
    prompts = load_settings().prompts
    user_bits = [prompts.day_brief_user_header]
    if calendar:
        user_bits.append("Calendar snapshot:\n" + calendar.summary_md.strip())
    if gmail:
        user_bits.append("Gmail snapshot:\n" + gmail.summary_md.strip())
    user = "\n\n".join(user_bits)
    if include_shared_context:
        bundle = build_shared_context()
        user = append_context_to_user_message(user, bundle)

    try:
        provider = get_llm_provider()
        result = provider.complete(
            [
                ChatMessage(role="system", content=prompts.day_brief_system),
                ChatMessage(role="user", content=user),
            ],
            max_tokens=400,
        )
        md = result.content.strip() + "\n"
        try:
            save_snapshot(DAY_BRIEF_SNAPSHOT_ID, md)
        except Exception:  # noqa: BLE001
            logger.exception("Failed to persist day-brief snapshot")
        return {
            "markdown": md,
            "sources": base["sources"],
            "partial": base["partial"],
            "empty": False,
            "llm": True,
            "model": result.model,
        }
    except LLMError as exc:
        return {
            **base,
            "error": str(exc),
            "markdown": base["markdown"],
        }
