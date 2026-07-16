"""Operator playbooks for Sender Inbox / ASX desks (Sprint 20)."""

from __future__ import annotations

import json
import threading
import uuid
from datetime import UTC, datetime
from typing import Any

from crawley.data.paths import DATA_DIR, ensure_data_dirs

_lock = threading.RLock()

DEFAULT_PLAYBOOKS: list[dict[str, Any]] = [
    {
        "id": "morning-mail",
        "name": "Morning mail triage",
        "desk": "gmail",
        "actions": ["start_ingest"],
        "note": "Start Sender Inbox one-at-a-time ingest up to current cap.",
    },
    {
        "id": "asx-morning",
        "name": "ASX scan + refresh recs",
        "desk": "investment",
        "actions": ["start_scan", "refresh_recommendations"],
        "note": "Scan active set, then regenerate recommendations when profiles exist.",
    },
]


def _path():
    ensure_data_dirs()
    return DATA_DIR / "playbooks.json"


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_playbooks() -> list[dict[str, Any]]:
    with _lock:
        path = _path()
        if not path.exists():
            save_playbooks(list(DEFAULT_PLAYBOOKS))
            return list(DEFAULT_PLAYBOOKS)
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return list(DEFAULT_PLAYBOOKS)
        rows = list(raw) if isinstance(raw, list) else []
        return rows or list(DEFAULT_PLAYBOOKS)


def save_playbooks(rows: list[dict[str, Any]]) -> None:
    with _lock:
        path = _path()
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        tmp.replace(path)


def upsert_playbook(
    *,
    name: str,
    desk: str,
    actions: list[str],
    note: str = "",
    playbook_id: str = "",
) -> dict[str, Any]:
    name = (name or "").strip()[:80]
    desk = (desk or "investment").strip().lower()
    if desk not in {"gmail", "investment"}:
        desk = "investment"
    if not name:
        raise ValueError("Playbook name is required.")
    actions = [a.strip() for a in actions if a.strip()]
    if not actions:
        raise ValueError("At least one action is required.")
    rows = load_playbooks()
    pid = (playbook_id or "").strip() or uuid.uuid4().hex[:10]
    row = {
        "id": pid,
        "name": name,
        "desk": desk,
        "actions": actions,
        "note": (note or "").strip()[:240],
        "updated_at": _now_iso(),
    }
    out = []
    replaced = False
    for r in rows:
        if r.get("id") == pid:
            out.append(row)
            replaced = True
        else:
            out.append(r)
    if not replaced:
        out.append(row)
    save_playbooks(out)
    return row


def delete_playbook(playbook_id: str) -> bool:
    rows = load_playbooks()
    kept = [r for r in rows if r.get("id") != playbook_id]
    if len(kept) == len(rows):
        return False
    save_playbooks(kept)
    return True


def run_playbook(playbook_id: str, executor) -> tuple[bool, str, list[str]]:
    """Execute playbook actions; returns (ok, message, action_log)."""
    rows = {r["id"]: r for r in load_playbooks() if r.get("id")}
    pb = rows.get(playbook_id)
    if not pb:
        return False, "Playbook not found.", []

    log: list[str] = []
    desk = pb.get("desk")
    for action in pb.get("actions") or []:
        if desk == "gmail" and action == "start_ingest":
            from crawley.sender_inbox.worker import start_ingest

            ok, msg = start_ingest(executor)
            log.append(f"start_ingest: {msg}")
            if not ok and "already" not in msg.lower():
                return False, msg, log
        elif desk == "investment" and action == "start_scan":
            from crawley.asx_desk.worker import start_scan

            ok, msg = start_scan(executor)
            log.append(f"start_scan: {msg}")
            if not ok and "already" not in msg.lower() and "already scanned" not in msg.lower():
                # "already scanned" is ok for morning playbook — continue to recs
                if "scanned" in msg.lower():
                    continue
                return False, msg, log
        elif desk == "investment" and action == "refresh_recommendations":
            from crawley.asx_desk.worker import refresh_recommendations

            ok, msg = refresh_recommendations(executor)
            log.append(f"refresh_recommendations: {msg}")
            if not ok:
                return False, msg, log
        elif desk == "investment" and action == "refresh_events":
            from crawley.asx_desk.worker import refresh_events

            ok, msg = refresh_events(executor)
            log.append(f"refresh_events: {msg}")
            if not ok:
                return False, msg, log
        else:
            log.append(f"skip unknown action: {action}")

    return True, f"Playbook “{pb.get('name')}” started.", log
