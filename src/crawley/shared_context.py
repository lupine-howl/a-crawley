"""Thin cross-module shared context (snapshots + standing notes + history pins)."""

from __future__ import annotations

import json
import threading
from dataclasses import dataclass
from typing import Any

from crawley.data.paths import ensure_data_dirs
from crawley.data.snapshots import get_history_entry, load_snapshots

# Hard caps — never unbounded prompt growth.
MAX_STANDING_CHARS = 1200
MAX_SNAPSHOT_CHARS_EACH = 400
MAX_SNAPSHOT_MODULES = 6
MAX_BUNDLE_CHARS = 3500
MAX_PINS = 4
MAX_PIN_CHARS_EACH = 400

_lock = threading.Lock()


def _standing_path():
    from crawley.data.paths import DATA_DIR

    return DATA_DIR / "standing_notes.txt"


def _meta_path():
    from crawley.data.paths import DATA_DIR

    return DATA_DIR / "shared_context_meta.json"


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
    path = _standing_path()
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return ""


def save_standing_notes(notes: str) -> str:
    ensure_data_dirs()
    text = notes.strip()
    if len(text) > MAX_STANDING_CHARS:
        text = text[:MAX_STANDING_CHARS]
    with _lock:
        _standing_path().write_text(text + ("\n" if text else ""), encoding="utf-8")
    return text


def load_context_meta() -> dict[str, Any]:
    ensure_data_dirs()
    path = _meta_path()
    if not path.exists():
        return {"pins": []}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"pins": []}
    if not isinstance(raw, dict):
        return {"pins": []}
    pins = raw.get("pins") if isinstance(raw.get("pins"), list) else []
    return {"pins": pins}


def save_context_meta(meta: dict[str, Any]) -> None:
    ensure_data_dirs()
    with _lock:
        _meta_path().write_text(
            json.dumps(meta, indent=2) + "\n",
            encoding="utf-8",
        )


def list_pins() -> list[dict[str, Any]]:
    return list(load_context_meta().get("pins") or [])


def pin_history(entry_id: str) -> tuple[bool, str]:
    entry = get_history_entry(entry_id)
    if entry is None:
        return False, "History entry not found."
    meta = load_context_meta()
    pins = [p for p in meta.get("pins") or [] if p.get("id") != entry_id]
    pins.insert(
        0,
        {
            "id": entry_id,
            "module_id": entry.get("module_id"),
            "title": entry.get("title"),
            "updated_at": entry.get("updated_at"),
        },
    )
    meta["pins"] = pins[:MAX_PINS]
    save_context_meta(meta)
    return True, "Pinned into shared context."


def unpin_history(entry_id: str) -> None:
    meta = load_context_meta()
    meta["pins"] = [p for p in meta.get("pins") or [] if p.get("id") != entry_id]
    save_context_meta(meta)


def build_shared_context(
    *,
    module_ids: list[str] | None = None,
) -> SharedContextBundle:
    """
    Read model over recent successful snapshots + optional standing notes + pins.

    Never loads secrets, OAuth tokens, or API keys.
    """
    standing = load_standing_notes()
    if len(standing) > MAX_STANDING_CHARS:
        standing = standing[:MAX_STANDING_CHARS]

    snaps = load_snapshots()
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

    # Pinned history (opt-in depth) before live last-snapshots.
    for pin in list_pins()[:MAX_PINS]:
        entry = get_history_entry(str(pin.get("id") or ""))
        if not entry:
            continue
        body = (entry.get("summary_md") or "").strip()
        if not body:
            continue
        if len(body) > MAX_PIN_CHARS_EACH:
            body = body[:MAX_PIN_CHARS_EACH].rstrip() + "…"
            truncated = True
        mid = entry.get("module_id") or "history"
        slices.append({"module_id": f"{mid} (pinned)", "summary": body})
        parts.append(f"## Pinned history · {mid}\n{body}")

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
