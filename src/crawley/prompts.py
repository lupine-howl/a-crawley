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
    co_parenting_system: str = (
        "You help one parent skim their co-parenting handoff schedule. "
        "Markdown with ## What's next and ## Watch-outs. Sole-operator planning; "
        "not legal advice. Under 220 words."
    )
    co_parenting_user_header: str = "Upcoming handoff windows (bounded):"
    diy_system: str = (
        "You help plan a DIY/home project from notes. Markdown with "
        "## Next steps and ## Materials to consider. Manual shopping only; "
        "no checkout links. Under 250 words."
    )
    diy_user_header: str = "DIY project notes:"
    finance_system: str = (
        "You help with personal finance/tax planning notes. Markdown with "
        "## Topics to review, ## Questions for an advisor, ## Reminders. "
        "Not professional tax or financial advice. Under 250 words."
    )
    finance_user_header: str = "Finance / tax planning notes:"
    coding_system: str = (
        "You help prioritize personal coding/creative project notes. "
        "Markdown with ## Focus now, ## Next experiments, ## Parking. "
        "No CI or forge writes. Under 250 words."
    )
    coding_user_header: str = "Coding / creative project notes:"
    day_brief_system: str = (
        "Compose a short morning Day brief from Calendar and Gmail snapshot texts. "
        "Markdown with ## Today and ## Follow-ups. Do not invent events or emails "
        "that are not in the inputs. Under 200 words."
    )
    day_brief_user_header: str = "Snapshot inputs for today’s brief:"

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def prompts_from_dict(raw: dict | None) -> PromptSettings:
    base = PromptSettings()
    if not raw:
        return base

    def pick(key: str, default: str) -> str:
        return (raw.get(key) or default).strip() or default

    return PromptSettings(
        **{field: pick(field, getattr(base, field)) for field in base.to_dict()}
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


def build_fitness_user_message(
    *,
    header: str,
    goal: str,
    activity_import: str = "",
) -> str:
    parts = [header.rstrip(), goal.strip()]
    if activity_import.strip():
        parts.append("Imported activity (bounded local file; not medical data):")
        parts.append(activity_import.strip()[:4000])
    return "\n".join(parts) + "\n"


def build_work_user_message(*, header: str, notes: str) -> str:
    return f"{header.rstrip()}\n{notes.strip()}\n"


def build_co_parenting_user_message(*, header: str, schedule_lines: list[str]) -> str:
    return header.rstrip() + "\n" + "\n".join(schedule_lines)
