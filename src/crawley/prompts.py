"""Editable prompt templates for Investment / Gmail LLM calls."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class PromptSettings:
    investment_system: str = (
        "You are a careful personal research assistant. "
        "Summarize findings into short, actionable notes the user "
        "can apply manually. Not professional financial advice. "
        "Keep under 250 words."
    )
    investment_user_footer: str = (
        "Write a brief summary and 2–4 practical notes. Manual action only; "
        "no trade orders."
    )
    gmail_system: str = (
        "Summarize a skim of the user's recent inbox into a short "
        "digest they can act on manually. No send/reply. Under 200 words."
    )
    gmail_user_header: str = "Recent inbox (bounded):"

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def prompts_from_dict(raw: dict | None) -> PromptSettings:
    base = PromptSettings()
    if not raw:
        return base
    return PromptSettings(
        investment_system=(raw.get("investment_system") or base.investment_system).strip()
        or base.investment_system,
        investment_user_footer=(
            raw.get("investment_user_footer") or base.investment_user_footer
        ).strip()
        or base.investment_user_footer,
        gmail_system=(raw.get("gmail_system") or base.gmail_system).strip()
        or base.gmail_system,
        gmail_user_header=(raw.get("gmail_user_header") or base.gmail_user_header).strip()
        or base.gmail_user_header,
    )


def build_investment_user_message(
    *,
    query: str,
    source_lines: list[str],
    footer: str,
) -> str:
    chunks = [f"Query: {query}", "Sources (bounded):", *source_lines, footer]
    return "\n".join(chunks)


def build_gmail_user_message(*, header: str, inbox_lines: list[str]) -> str:
    return header.rstrip() + "\n" + "\n".join(inbox_lines)
