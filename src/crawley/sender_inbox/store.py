"""Persisted Sender Inbox PoC state under data/gmail/sender_inbox/."""

from __future__ import annotations

import json
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from crawley.data.paths import ensure_data_dirs
from crawley.sender_inbox.schema import (
    POC_CAP,
    normalize_metrics,
    sender_id_for,
    signal_chips,
    sort_weight,
)

_lock = threading.RLock()


def inbox_dir() -> Path:
    from crawley.data.paths import GMAIL_DIR

    ensure_data_dirs()
    path = GMAIL_DIR / "sender_inbox"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _path(name: str) -> Path:
    return inbox_dir() / name


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def default_ingest_state() -> dict[str, Any]:
    return {
        "status": "idle",  # idle | busy | paused | done | error
        "cap": POC_CAP,
        "processed": 0,
        "current_line": "",
        "last_error": "",
        "message_errors": [],  # [{id, subject, error}]
        "pause_requested": False,
        "updated_at": "",
    }


def load_ingest_state() -> dict[str, Any]:
    with _lock:
        state = default_ingest_state()
        raw = _read_json(_path("ingest_state.json"), {})
        if isinstance(raw, dict):
            state.update(raw)
        state["cap"] = int(state.get("cap") or POC_CAP)
        state["processed"] = len(load_messages())
        return state


def save_ingest_state(state: dict[str, Any]) -> None:
    with _lock:
        state = {**state, "updated_at": _now_iso(), "processed": len(load_messages())}
        _write_json(_path("ingest_state.json"), state)


def load_messages() -> list[dict[str, Any]]:
    with _lock:
        raw = _read_json(_path("messages.json"), [])
        return list(raw) if isinstance(raw, list) else []


def save_messages(messages: list[dict[str, Any]]) -> None:
    with _lock:
        _write_json(_path("messages.json"), messages)


def load_profiles() -> dict[str, Any]:
    with _lock:
        raw = _read_json(_path("profiles.json"), {})
        return dict(raw) if isinstance(raw, dict) else {}


def save_profiles(profiles: dict[str, Any]) -> None:
    with _lock:
        _write_json(_path("profiles.json"), profiles)


def load_todos() -> list[dict[str, Any]]:
    with _lock:
        raw = _read_json(_path("todos.json"), [])
        return list(raw) if isinstance(raw, list) else []


def save_todos(todos: list[dict[str, Any]]) -> None:
    with _lock:
        _write_json(_path("todos.json"), todos)


def upsert_message(message: dict[str, Any]) -> None:
    with _lock:
        messages = load_messages()
        by_id = {m["id"]: m for m in messages if m.get("id")}
        by_id[message["id"]] = message
        save_messages(list(by_id.values()))
        state = load_ingest_state()
        state["processed"] = len(by_id)
        save_ingest_state(state)


def ingested_ids() -> set[str]:
    return {m["id"] for m in load_messages() if m.get("id")}


def remaining_capacity() -> int:
    state = load_ingest_state()
    return max(0, int(state["cap"]) - len(load_messages()))


def reset_poc_data() -> None:
    with _lock:
        save_messages([])
        save_profiles({})
        save_todos([])
        state = default_ingest_state()
        state["status"] = "idle"
        state["current_line"] = ""
        state["last_error"] = ""
        state["message_errors"] = []
        state["pause_requested"] = False
        save_ingest_state(state)


def group_senders() -> list[dict[str, Any]]:
    """Sender list rows: most recent activity first, urgency boost."""
    messages = load_messages()
    profiles = load_profiles()
    todos = load_todos()
    groups: dict[str, dict[str, Any]] = {}
    for msg in messages:
        sid = msg.get("sender_id") or sender_id_for(msg.get("from_addr", ""))
        g = groups.get(sid)
        if g is None:
            g = {
                "sender_id": sid,
                "from_name": msg.get("from_name") or "",
                "from_addr": msg.get("from_addr") or "",
                "messages": [],
                "latest_at": msg.get("internal_date") or "",
                "open_todos": 0,
            }
            groups[sid] = g
        g["messages"].append(msg)
        if (msg.get("internal_date") or "") > (g["latest_at"] or ""):
            g["latest_at"] = msg.get("internal_date") or ""
            if msg.get("from_name"):
                g["from_name"] = msg.get("from_name") or g["from_name"]
            if msg.get("from_addr"):
                g["from_addr"] = msg.get("from_addr") or g["from_addr"]

    todo_open: dict[str, int] = {}
    for t in todos:
        if not t.get("done"):
            todo_open[t.get("sender_id", "")] = todo_open.get(t.get("sender_id", ""), 0) + 1

    rows: list[dict[str, Any]] = []
    for sid, g in groups.items():
        # Aggregate signal chips from newest messages first.
        chips: list[str] = []
        boost = 0
        for msg in sorted(g["messages"], key=lambda m: m.get("internal_date") or "", reverse=True):
            boost = max(boost, sort_weight(msg.get("metrics")))
            for chip in signal_chips(msg.get("metrics")):
                if chip not in chips:
                    chips.append(chip)
            if len(chips) >= 3:
                break
        profile = profiles.get(sid) or {}
        rows.append(
            {
                "sender_id": sid,
                "from_name": g["from_name"],
                "from_addr": g["from_addr"],
                "display_name": g["from_name"] or g["from_addr"] or "Unknown sender",
                "message_count": len(g["messages"]),
                "latest_at": g["latest_at"],
                "signals": chips[:3],
                "open_todos": todo_open.get(sid, 0),
                "has_profile": bool(profile.get("markdown")),
                "_sort": (boost, g["latest_at"] or ""),
            }
        )
    rows.sort(key=lambda r: r["_sort"], reverse=True)
    for r in rows:
        r.pop("_sort", None)
    return rows


def sender_detail(sender_id: str) -> dict[str, Any] | None:
    messages = [m for m in load_messages() if m.get("sender_id") == sender_id]
    if not messages:
        return None
    messages.sort(key=lambda m: m.get("internal_date") or "", reverse=True)
    first = messages[0]
    profile = load_profiles().get(sender_id) or {
        "markdown": "",
        "status": "empty",
        "error": "",
        "updated_at": "",
    }
    todos = [t for t in load_todos() if t.get("sender_id") == sender_id]
    todos.sort(key=lambda t: (bool(t.get("done")), t.get("created_at") or ""))
    return {
        "sender_id": sender_id,
        "from_name": first.get("from_name") or "",
        "from_addr": first.get("from_addr") or "",
        "display_name": first.get("from_name") or first.get("from_addr") or "Unknown sender",
        "message_count": len(messages),
        "messages": [
            {
                **m,
                "signals": signal_chips(m.get("metrics")),
            }
            for m in messages
        ],
        "profile": profile,
        "todos": todos,
        "open_todo_count": sum(1 for t in todos if not t.get("done")),
    }


def progress_view(*, running: bool | None = None) -> dict[str, Any]:
    state = load_ingest_state()
    processed = len(load_messages())
    cap = int(state.get("cap") or POC_CAP)
    remaining = max(0, cap - processed)
    status = state.get("status") or "idle"
    if running is True:
        status = "busy"
    elif running is False and status == "busy":
        # Process restarted mid-ingest — surface as paused so Resume works.
        status = "paused"
        state["status"] = "paused"
        save_ingest_state(state)
    return {
        **state,
        "status": status,
        "processed": processed,
        "cap": cap,
        "remaining": remaining,
        "sender_count": len(group_senders()),
    }


def toggle_todo(todo_id: str) -> dict[str, Any] | None:
    with _lock:
        todos = load_todos()
        found = None
        for t in todos:
            if t.get("id") == todo_id:
                t["done"] = not bool(t.get("done"))
                found = t
                break
        if found is None:
            return None
        save_todos(todos)
        return found
