"""Display helpers for Sender Inbox UI."""

from __future__ import annotations

from datetime import UTC, datetime


def relative_time(iso: str | None) -> str:
    if not iso:
        return "—"
    try:
        raw = iso.replace("Z", "+00:00")
        when = datetime.fromisoformat(raw)
        if when.tzinfo is None:
            when = when.replace(tzinfo=UTC)
        now = datetime.now(UTC)
        delta = now - when.astimezone(UTC)
        secs = int(delta.total_seconds())
        if secs < 60:
            return "just now"
        if secs < 3600:
            return f"{secs // 60}m ago"
        if secs < 86400:
            return f"{secs // 3600}h ago"
        if secs < 86400 * 14:
            return f"{secs // 86400}d ago"
        return when.date().isoformat()
    except ValueError:
        return iso[:16]
