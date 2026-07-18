"""Persist last successful module summaries + bounded history (Sprint 15)."""

from __future__ import annotations

import json
import threading
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from crawley.data.paths import ensure_data_dirs

MAX_HISTORY_PER_MODULE = 20
_lock = threading.Lock()


def _snapshots_path():
    from crawley.data.paths import DATA_DIR

    return DATA_DIR / "snapshots.json"


def _history_path():
    from crawley.data.paths import DATA_DIR

    return DATA_DIR / "snapshot_history.json"


@dataclass
class ModuleSnapshot:
    module_id: str
    summary_md: str
    updated_at: str
    status: str = "done"

    def to_dict(self) -> dict[str, str]:
        return {
            "module_id": self.module_id,
            "summary_md": self.summary_md,
            "updated_at": self.updated_at,
            "status": self.status,
        }


def _load_raw() -> dict[str, Any]:
    ensure_data_dirs()
    path = _snapshots_path()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def load_snapshots() -> dict[str, ModuleSnapshot]:
    raw = _load_raw()
    out: dict[str, ModuleSnapshot] = {}
    for module_id, entry in raw.items():
        if not isinstance(entry, dict):
            continue
        summary = (entry.get("summary_md") or "").strip()
        if not summary:
            continue
        out[module_id] = ModuleSnapshot(
            module_id=module_id,
            summary_md=summary,
            updated_at=str(entry.get("updated_at") or ""),
            status=str(entry.get("status") or "done"),
        )
    return out


def get_snapshot(module_id: str) -> ModuleSnapshot | None:
    return load_snapshots().get(module_id)


def _load_history_raw() -> dict[str, list[dict[str, Any]]]:
    ensure_data_dirs()
    path = _history_path()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _append_history(module_id: str, snap: ModuleSnapshot) -> None:
    """Bounded N per module; newest first. Retention: keep last MAX_HISTORY_PER_MODULE."""
    hist = _load_history_raw()
    rows = list(hist.get(module_id) or [])
    entry = {
        "id": str(uuid.uuid4()),
        "module_id": module_id,
        "summary_md": snap.summary_md,
        "updated_at": snap.updated_at,
        "status": snap.status,
        "title": (snap.summary_md.splitlines()[0] if snap.summary_md else module_id)[:120],
    }
    rows.insert(0, entry)
    hist[module_id] = rows[:MAX_HISTORY_PER_MODULE]
    _history_path().write_text(json.dumps(hist, indent=2) + "\n", encoding="utf-8")


def list_history(
    *,
    module_id: str | None = None,
    query: str = "",
    limit: int = 50,
) -> list[dict[str, Any]]:
    hist = _load_history_raw()
    items: list[dict[str, Any]] = []
    keys = [module_id] if module_id else sorted(hist.keys())
    for mid in keys:
        for row in hist.get(mid) or []:
            items.append(row)
    items.sort(key=lambda r: r.get("updated_at") or "", reverse=True)
    q = (query or "").strip().lower()
    if q:
        items = [
            r
            for r in items
            if q in (r.get("title") or "").lower()
            or q in (r.get("summary_md") or "").lower()
            or q in (r.get("module_id") or "").lower()
        ]
    return items[:limit]


def get_history_entry(entry_id: str) -> dict[str, Any] | None:
    for row in list_history(limit=500):
        if row.get("id") == entry_id:
            return row
    return None


def save_snapshot(module_id: str, summary_md: str, *, status: str = "done") -> ModuleSnapshot:
    """Overwrite latest snapshot and append to bounded history."""
    summary = (summary_md or "").strip()
    if not summary:
        raise ValueError("Cannot save empty snapshot")
    snap = ModuleSnapshot(
        module_id=module_id,
        summary_md=summary,
        updated_at=datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        status=status,
    )
    with _lock:
        data = _load_raw()
        data[module_id] = snap.to_dict()
        _snapshots_path().write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        _append_history(module_id, snap)
    return snap
