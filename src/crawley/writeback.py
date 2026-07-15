"""Write-back dry-run audit trail (local filesystem)."""

from __future__ import annotations

import json
import threading
from datetime import UTC, datetime
from typing import Any

from crawley.data.paths import DATA_DIR, ensure_data_dirs

AUDIT_PATH = DATA_DIR / "writeback_audit.jsonl"
_lock = threading.Lock()


def record_dry_run(
    *,
    module_id: str,
    stage: str,
    draft: dict[str, Any],
    note: str = "",
) -> dict[str, Any]:
    """Append one dry-run audit row. Never performs a remote mutation."""
    ensure_data_dirs()
    entry = {
        "at": datetime.now(UTC).isoformat(),
        "module_id": module_id,
        "stage": stage,
        "dry_run": True,
        "draft": draft,
        "note": note,
    }
    with _lock:
        with AUDIT_PATH.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry
