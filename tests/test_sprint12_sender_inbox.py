"""Sprint 12 — Sender Inbox PoC."""

from __future__ import annotations

from unittest.mock import MagicMock

from fastapi.testclient import TestClient

import crawley.sender_inbox.llm_tasks as llm_tasks
import crawley.sender_inbox.store as store
from crawley.sender_inbox.schema import (
    POC_CAP,
    normalize_metrics,
    sender_id_for,
    signal_chips,
)
from crawley.sender_inbox.worker import start_ingest


def test_settings_and_gmail_show_sender_inbox(client: TestClient) -> None:
    resp = client.get("/modules/gmail")
    assert resp.status_code == 200
    assert "Sender Inbox" in resp.text
    assert (
        "Start ingest" in resp.text
        or "Connect Google" in resp.text
        or "GOOGLE_CLIENT" in resp.text
    )


def test_metric_schema_normalization() -> None:
    m = normalize_metrics(
        {
            "urgency": "HIGH",
            "requires_reply": True,
            "action_needed": False,
            "vip": True,
            "category": "Work",
            "signals": ["Reply", "odd!"],
            "brief": "Need a decision",
        }
    )
    assert m["urgency"] == "high"
    assert m["category"] == "work"
    assert m["requires_reply"] is True
    assert "urgent" in m["signals"]
    assert "reply" in m["signals"]
    assert "vip" in m["signals"]
    chips = signal_chips(m, limit=3)
    assert len(chips) <= 3
    assert chips[0] in {"urgent", "reply", "vip"}


def test_group_senders_and_persistence(tmp_path, monkeypatch) -> None:
    import crawley.data.paths as paths

    data = tmp_path / "data"
    monkeypatch.setattr(paths, "DATA_DIR", data)
    monkeypatch.setattr(paths, "GMAIL_DIR", data / "gmail")

    sid = sender_id_for("jane@example.com")
    store.upsert_message(
        {
            "id": "m1",
            "thread_id": "t1",
            "from_name": "Jane",
            "from_addr": "jane@example.com",
            "sender_id": sid,
            "subject": "Quote",
            "snippet": "Please reply",
            "body_text": "Please reply with the quote",
            "internal_date": "2026-07-15T10:00:00Z",
            "metrics": normalize_metrics(
                {"urgency": "high", "requires_reply": True, "brief": "Need reply"}
            ),
            "error": None,
            "ingested_at": "2026-07-15T10:01:00Z",
        }
    )
    store.save_todos(
        [
            {
                "id": "todo-1",
                "sender_id": sid,
                "text": "Reply with quote",
                "from_subject": "Quote",
                "message_id": "m1",
                "done": False,
                "created_at": "2026-07-15T10:02:00Z",
            }
        ]
    )
    store.save_profiles(
        {
            sid: {
                "markdown": "## Relationship\nClient.",
                "status": "ready",
                "error": "",
                "updated_at": "2026-07-15T10:03:00Z",
            }
        }
    )

    rows = store.group_senders()
    assert len(rows) == 1
    assert rows[0]["from_addr"] == "jane@example.com"
    assert rows[0]["open_todos"] == 1
    assert "reply" in rows[0]["signals"] or "urgent" in rows[0]["signals"]

    detail = store.sender_detail(sid)
    assert detail is not None
    assert detail["profile"]["markdown"].startswith("## Relationship")
    assert detail["todos"][0]["text"] == "Reply with quote"

    toggled = store.toggle_todo("todo-1")
    assert toggled is not None and toggled["done"] is True
    assert store.sender_detail(sid)["open_todo_count"] == 0

    # Survive "restart" via reload from disk.
    assert (data / "gmail" / "sender_inbox" / "messages.json").exists()
    store.reset_poc_data()
    assert store.load_messages() == []
    assert store.remaining_capacity() == POC_CAP


def test_extract_json_from_llm_text() -> None:
    raw = llm_tasks.extract_json('Here you go:\n```json\n{"urgency":"low"}\n```')
    assert raw["urgency"] == "low"
    arr = llm_tasks.extract_json('[{"text":"Do thing"}]')
    assert arr[0]["text"] == "Do thing"


def test_inbox_start_requires_auth(client: TestClient) -> None:
    resp = client.post("/modules/gmail/inbox/start", headers={"HX-Request": "true"})
    assert resp.status_code == 200
    # Without Google token, start fails politely and panel still renders.
    assert "Sender Inbox" in resp.text


def test_sender_detail_route(client: TestClient) -> None:
    # client fixture already redirects DATA_DIR / GMAIL_DIR into tmp_path
    sid = sender_id_for("a@b.com")
    store.upsert_message(
        {
            "id": "x1",
            "thread_id": "",
            "from_name": "Alex",
            "from_addr": "a@b.com",
            "sender_id": sid,
            "subject": "Hi",
            "snippet": "Hello",
            "body_text": "Hello there",
            "internal_date": "2026-07-15T12:00:00Z",
            "metrics": normalize_metrics({"urgency": "low", "brief": "Hi"}),
            "error": None,
            "ingested_at": "2026-07-15T12:00:00Z",
        }
    )
    store.save_profiles(
        {
            sid: {
                "markdown": "Profile body",
                "status": "ready",
                "error": "",
                "updated_at": "2026-07-15T12:01:00Z",
            }
        }
    )
    resp = client.get(f"/modules/gmail/senders/{sid}")
    assert resp.status_code == 200
    assert "Alex" in resp.text
    assert "Profile" in resp.text
    assert "Messages in bundle" in resp.text


def test_worker_isolates_message_error(monkeypatch, tmp_path) -> None:
    import crawley.data.paths as paths
    import crawley.sender_inbox.fetch as fetch
    import crawley.sender_inbox.worker as worker

    data = tmp_path / "data"
    monkeypatch.setattr(paths, "DATA_DIR", data)
    monkeypatch.setattr(paths, "GMAIL_DIR", data / "gmail")

    store.reset_poc_data()
    state = store.load_ingest_state()
    state["cap"] = 1
    store.save_ingest_state(state)

    monkeypatch.setattr(worker, "load_credentials", lambda: object())
    monkeypatch.setattr(
        fetch, "list_candidate_ids", lambda creds, max_results=50: ["bad1"]
    )

    def boom(*args, **kwargs):
        raise ValueError("llm exploded")

    monkeypatch.setattr(fetch, "fetch_message", boom)

    class ImmediateExecutor:
        def submit(self, fn, *args, **kwargs):
            fn(*args, **kwargs)
            return MagicMock()

    ok, _ = start_ingest(ImmediateExecutor())
    assert ok is True
    msgs = store.load_messages()
    assert len(msgs) == 1
    assert msgs[0]["error"]
    progress = store.progress_view(running=False)
    assert progress["processed"] == 1
