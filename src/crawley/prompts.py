"""Editable prompt templates for module LLM calls."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class PromptSettings:
    investment_system: str = (
        "You are a careful personal research assistant. "
        "Summarize findings into short, actionable notes the user "
        "can apply manually. Not professional financial advice. "
        "Structure Markdown with: what's moving, risks, and a short watch list. "
        "Keep under 280 words. Never propose trade orders."
    )
    investment_user_footer: str = (
        "Write Markdown sections: What's moving / Risks / Watch list. "
        "Manual action only; no trade orders."
    )
    gmail_system: str = (
        "Summarize a skim of the user's recent inbox into Markdown with "
        "## Priorities and ## Follow-ups sections. "
        "They act manually — no send/reply. Under 220 words."
    )
    gmail_user_header: str = "Recent inbox (bounded):"
    calendar_system: str = (
        "Summarize upcoming calendar events into a short Markdown brief: "
        "what's coming up, conflicts/pressure points, and gentle prep notes. "
        "Read-only — no invites or edits. Under 220 words."
    )
    calendar_user_header: str = "Upcoming events (bounded):"
    fitness_system: str = (
        "You help with personal fitness planning. Produce Markdown with an "
        "introductory breakdown: habits to start, a gentle weekly starter plan, "
        "and progress checks. Not medical advice; do not diagnose. Under 280 words."
    )
    fitness_user_header: str = "User goal (personal planning only):"
    work_system: str = (
        "You help prioritize personal work tasks from a notes dump. "
        "Produce Markdown with ## Top priorities, ## Next actions, and ## Parking. "
        "Assume a single operator; no ticket-system writes. Under 250 words."
    )
    work_user_header: str = "This week’s notes / tasks:"

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def prompts_from_dict(raw: dict | None) -> PromptSettings:
    base = PromptSettings()
    if not raw:
        return base

    def pick(key: str, default: str) -> str:
        return (raw.get(key) or default).strip() or default

    return PromptSettings(
        investment_system=pick("investment_system", base.investment_system),
        investment_user_footer=pick(
            "investment_user_footer", base.investment_user_footer
        ),
        gmail_system=pick("gmail_system", base.gmail_system),
        gmail_user_header=pick("gmail_user_header", base.gmail_user_header),
        calendar_system=pick("calendar_system", base.calendar_system),
        calendar_user_header=pick("calendar_user_header", base.calendar_user_header),
        fitness_system=pick("fitness_system", base.fitness_system),
        fitness_user_header=pick("fitness_user_header", base.fitness_user_header),
        work_system=pick("work_system", base.work_system),
        work_user_header=pick("work_user_header", base.work_user_header),
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


def build_calendar_user_message(*, header: str, event_lines: list[str]) -> str:
    return header.rstrip() + "\n" + "\n".join(event_lines)


def build_fitness_user_message(*, header: str, goal: str) -> str:
    return f"{header.rstrip()}\n{goal.strip()}\n"


def build_work_user_message(*, header: str, notes: str) -> str:
    return f"{header.rstrip()}\n{notes.strip()}\n"
