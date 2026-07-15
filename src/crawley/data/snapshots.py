"""Persist last successful module summaries for the home glance."""

from __future__ import annotations

import json
import threading
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from crawley.data.paths import DATA_DIR, ensure_data_dirs

SNAPSHOTS_PATH = DATA_DIR / "snapshots.json"
_lock = threading.Lock()


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
    if not SNAPSHOTS_PATH.exists():
        return {}
    try:
        data = json.loads(SNAPSHOTS_PATH.read_text(encoding="utf-8"))
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


def save_snapshot(module_id: str, summary_md: str, *, status: str = "done") -> ModuleSnapshot:
    """Overwrite snapshot for a successful run only (caller responsibility)."""
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
        SNAPSHOTS_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return snap
