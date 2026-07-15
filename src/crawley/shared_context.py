"""Thin cross-module shared context (snapshots + standing notes)."""

from __future__ import annotations

import json
import threading
from dataclasses import dataclass
from typing import Any

from crawley.data.paths import DATA_DIR, ensure_data_dirs
from crawley.data.snapshots import load_snapshots

STANDING_NOTES_PATH = DATA_DIR / "standing_notes.txt"
CONTEXT_META_PATH = DATA_DIR / "shared_context_meta.json"

# Hard caps — never unbounded prompt growth.
MAX_STANDING_CHARS = 1200
MAX_SNAPSHOT_CHARS_EACH = 400
MAX_SNAPSHOT_MODULES = 6
MAX_BUNDLE_CHARS = 3500

_lock = threading.Lock()


@dataclass
class SharedContextBundle:
    standing_notes: str
    snapshot_slices: list[dict[str, str]]
    text: str
    truncated: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "standing_notes": self.standing_notes,
            "snapshot_slices": self.snapshot_slices,
            "text": self.text,
            "truncated": self.truncated,
            "char_len": len(self.text),
        }


def load_standing_notes() -> str:
    ensure_data_dirs()
    if STANDING_NOTES_PATH.exists():
        return STANDING_NOTES_PATH.read_text(encoding="utf-8").strip()
    return ""


def save_standing_notes(notes: str) -> str:
    ensure_data_dirs()
    text = notes.strip()
    if len(text) > MAX_STANDING_CHARS:
        text = text[:MAX_STANDING_CHARS]
    with _lock:
        STANDING_NOTES_PATH.write_text(text + ("\n" if text else ""), encoding="utf-8")
    return text


def build_shared_context(
    *,
    module_ids: list[str] | None = None,
) -> SharedContextBundle:
    """
    Read model over recent successful snapshots + optional standing notes.

    Never loads secrets, OAuth tokens, or API keys.
    """
    standing = load_standing_notes()
    if len(standing) > MAX_STANDING_CHARS:
        standing = standing[:MAX_STANDING_CHARS]

    snaps = load_snapshots()
    # Prefer newest-looking by updated_at when present.
    items = list(snaps.values())
    items.sort(key=lambda s: s.updated_at or "", reverse=True)
    if module_ids is not None:
        allow = set(module_ids)
        items = [s for s in items if s.module_id in allow]

    slices: list[dict[str, str]] = []
    parts: list[str] = []
    truncated = False

    if standing:
        parts.append("## Standing notes\n" + standing)

    for snap in items[:MAX_SNAPSHOT_MODULES]:
        body = (snap.summary_md or "").strip()
        if not body:
            continue
        if len(body) > MAX_SNAPSHOT_CHARS_EACH:
            body = body[:MAX_SNAPSHOT_CHARS_EACH].rstrip() + "…"
            truncated = True
        slices.append({"module_id": snap.module_id, "summary": body})
        parts.append(f"## Snapshot · {snap.module_id}\n{body}")

    text = "\n\n".join(parts).strip()
    if len(text) > MAX_BUNDLE_CHARS:
        text = text[:MAX_BUNDLE_CHARS].rstrip() + "\n…"
        truncated = True

    return SharedContextBundle(
        standing_notes=standing,
        snapshot_slices=slices,
        text=text,
        truncated=truncated,
    )


def append_context_to_user_message(user: str, bundle: SharedContextBundle) -> str:
    if not bundle.text:
        return user
    return (
        user.rstrip()
        + "\n\n---\nOptional shared context (local; size-capped; no secrets):\n"
        + bundle.text
        + "\n"
    )
