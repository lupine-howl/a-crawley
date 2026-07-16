"""Sprint 34 — gmail-ingest daemon + /v1/gmail Sender Inbox API."""

from __future__ import annotations

from fastapi.testclient import TestClient

import crawley.sender_inbox.store as store
from crawley.daemons import gmail_ingest
from crawley.sender_inbox import worker
from crawley.sender_inbox.schema import normalize_metrics, sender_id_for


def _seed_sender() -> str:
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
    store.save_profiles(
        {
            sid: {
                "markdown": "## Jane\nNeeds a quote reply.",
                "status": "ready",
                "error": "",
                "updated_at": "2026-07-15T10:02:00Z",
            }
        }
    )
    return sid


def test_external_mode_queues_instead_of_running(client: TestClient, monkeypatch) -> None:
    monkeypatch.setenv("CRAWLEY_GMAIL_WORKER", "daemon")
    store.reset_poc_data()
    monkeypatch.setattr(worker, "load_credentials", lambda: object())

    submitted: list[object] = []

    class FakeExec:
        def submit(self, fn, *a, **k):
            submitted.append(fn)
            return None

    monkeypatch.setattr(client.app.state, "executor", FakeExec())

    resp = client.post("/v1/gmail/ingest/start", json={"force": True})
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    assert "queued" in body["message"].lower() or body["job"]["status"] == "queued"
    assert submitted == []

    state = store.load_ingest_state()
    assert state.get("start_requested") is True
    assert state.get("status") == "queued"

    health = client.get("/health").json()
    assert health["gmail_worker"] == "daemon"


def test_daemon_claims_queued_ingest(tmp_path, monkeypatch) -> None:
    import crawley.data.paths as paths

    data = tmp_path / "data"
    monkeypatch.setattr(paths, "DATA_DIR", data)
    monkeypatch.setattr(paths, "GMAIL_DIR", data / "gmail")
    monkeypatch.setenv("CRAWLEY_GMAIL_WORKER", "daemon")
    monkeypatch.setattr(worker, "load_credentials", lambda: object())

    store.reset_poc_data()
    ok, msg = worker.queue_ingest_for_daemon(force=True)
    assert ok, msg
    assert worker.claim_queued_ingest() is True

    ran: list[bool] = []

    def fake_body() -> None:
        ran.append(True)
        state = store.load_ingest_state()
        state["status"] = "idle"
        state["current_line"] = "done"
        store.save_ingest_state(state)
        worker._running = False  # noqa: SLF001

    monkeypatch.setattr(worker, "_worker_body", fake_body)
    ok2, msg2 = worker.run_ingest_in_this_process(force=False)
    assert ok2, msg2
    assert ran == [True]
    assert store.load_ingest_state().get("start_requested") is False


def test_stop_cancels_queued(client: TestClient, monkeypatch) -> None:
    monkeypatch.setenv("CRAWLEY_GMAIL_WORKER", "daemon")
    store.reset_poc_data()
    monkeypatch.setattr(worker, "load_credentials", lambda: object())
    assert client.post("/v1/gmail/ingest/start", json={"force": True}).json()["ok"] is True
    stop = client.post("/v1/gmail/ingest/stop")
    assert stop.status_code == 200
    assert stop.json()["ok"] is True
    state = store.load_ingest_state()
    assert not state.get("start_requested")
    assert state.get("status") != "queued"


def test_senders_api_and_job(client: TestClient, monkeypatch) -> None:
    sid = _seed_sender()
    import crawley.google_oauth as google_oauth

    monkeypatch.setattr(
        google_oauth,
        "google_auth_status",
        lambda: {"connected": True, "client_ok": True, "error": None},
    )

    listing = client.get("/v1/gmail/senders")
    assert listing.status_code == 200
    body = listing.json()
    assert body["count"] >= 1
    assert any(s["sender_id"] == sid for s in body["senders"])

    detail = client.get(f"/v1/gmail/senders/{sid}")
    assert detail.status_code == 200
    d = detail.json()
    assert "Jane" in d["profile"]["markdown"]
    assert d["message_count"] == 1

    job = client.get("/v1/jobs/gmail-ingest")
    assert job.status_code == 200
    assert job.json()["id"] == "gmail-ingest"

    conn = client.get("/v1/gmail/connection")
    assert conn.status_code == 200
    assert conn.json()["oauth_start_path"].startswith("/modules/gmail/oauth")


def test_cli_parser() -> None:
    parser = gmail_ingest.build_parser()
    args = parser.parse_args(["status"])
    assert args.command == "status"
    args2 = parser.parse_args(["once", "--force"])
    assert args2.force is True
