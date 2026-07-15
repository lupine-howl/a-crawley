"""Write-back audit trail (local filesystem)."""

from __future__ import annotations

import json
import threading
from datetime import UTC, datetime
from typing import Any

from crawley.data.paths import DATA_DIR, ensure_data_dirs

AUDIT_PATH = DATA_DIR / "writeback_audit.jsonl"
_lock = threading.Lock()


def record_audit(
    *,
    module_id: str,
    stage: str,
    draft: dict[str, Any],
    note: str = "",
    dry_run: bool = False,
    success: bool | None = None,
) -> dict[str, Any]:
    """Append one audit row (dry-run or live attempt)."""
    ensure_data_dirs()
    entry = {
        "at": datetime.now(UTC).isoformat(),
        "module_id": module_id,
        "stage": stage,
        "dry_run": dry_run,
        "success": success,
        "draft": draft,
        "note": note,
        "action_summary": _summarize(draft, stage=stage, dry_run=dry_run, success=success),
    }
    with _lock:
        with AUDIT_PATH.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def record_dry_run(
    *,
    module_id: str,
    stage: str,
    draft: dict[str, Any],
    note: str = "",
) -> dict[str, Any]:
    """Append one dry-run audit row. Never performs a remote mutation."""
    return record_audit(
        module_id=module_id,
        stage=stage,
        draft=draft,
        note=note,
        dry_run=True,
        success=True,
    )


def _summarize(
    draft: dict[str, Any],
    *,
    stage: str,
    dry_run: bool,
    success: bool | None,
) -> str:
    action = draft.get("action") or stage
    title = ""
    payload = draft.get("payload") or {}
    if isinstance(payload, dict):
        title = str(payload.get("summary") or payload.get("title") or "")
    bits = [str(action)]
    if title:
        bits.append(title[:80])
    if dry_run:
        bits.append("dry-run")
    elif success is True:
        bits.append("ok")
    elif success is False:
        bits.append("failed")
    return " · ".join(bits)


def read_audit_entries(*, limit: int = 20) -> list[dict[str, Any]]:
    """Newest-first bounded audit entries for the Settings/Calendar viewer."""
    ensure_data_dirs()
    if not AUDIT_PATH.exists():
        return []
    rows: list[dict[str, Any]] = []
    try:
        lines = AUDIT_PATH.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
        if len(rows) >= limit:
            break
    return rows
