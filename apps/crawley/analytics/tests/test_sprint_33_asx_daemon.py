"""Sprint 33 — asx-scanner daemon entrypoint + API handoff."""

from __future__ import annotations

from fastapi.testclient import TestClient

import crawley.asx_desk.store as store
from crawley.asx_desk import worker
from crawley.daemons import asx_scanner


def test_external_mode_queues_instead_of_running(client: TestClient, monkeypatch) -> None:
    monkeypatch.setenv("CRAWLEY_ASX_WORKER", "daemon")
    store.reset_poc_data()
    store.set_poc_tickers(["CBA"])

    submitted: list[object] = []

    class FakeExec:
        def submit(self, fn, *a, **k):
            submitted.append(fn)
            return None

    monkeypatch.setattr(client.app.state, "executor", FakeExec())

    resp = client.post("/v1/asx/scan/start", json={"force": True})
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    assert "queued" in body["message"].lower() or body["job"]["status"] == "queued"
    assert submitted == []

    state = store.load_scan_state()
    assert state.get("start_requested") is True
    assert state.get("status") == "queued"

    health = client.get("/health").json()
    assert health["asx_worker"] == "daemon"


def test_daemon_claims_queued_scan(tmp_path, monkeypatch) -> None:
    import crawley.data.paths as paths

    data = tmp_path / "data"
    monkeypatch.setattr(paths, "DATA_DIR", data)
    monkeypatch.setattr(paths, "INVESTMENT_DIR", data / "investment")
    monkeypatch.setenv("CRAWLEY_ASX_WORKER", "daemon")

    store.reset_poc_data()
    store.set_poc_tickers(["CBA"])
    ok, msg = worker.queue_scan_for_daemon(force=True)
    assert ok, msg
    assert worker.claim_queued_scan() is True

    ran: list[bool] = []

    def fake_body() -> None:
        ran.append(True)
        state = store.load_scan_state()
        state["status"] = "idle"
        state["current_line"] = "done"
        store.save_scan_state(state)
        worker._running = False  # noqa: SLF001

    monkeypatch.setattr(worker, "_worker_body", fake_body)
    ok2, msg2 = worker.run_scan_in_this_process(force=False)
    assert ok2, msg2
    assert ran == [True]
    assert store.load_scan_state().get("start_requested") is False


def test_cli_status_and_once_help() -> None:
    parser = asx_scanner.build_parser()
    args = parser.parse_args(["status"])
    assert args.command == "status"
    args2 = parser.parse_args(["once", "--force"])
    assert args2.force is True


def test_stop_cancels_queued(client: TestClient, monkeypatch) -> None:
    monkeypatch.setenv("CRAWLEY_ASX_WORKER", "daemon")
    store.reset_poc_data()
    store.set_poc_tickers(["CBA"])
    assert client.post("/v1/asx/scan/start", json={"force": True}).json()["ok"] is True
    stop = client.post("/v1/asx/scan/stop")
    assert stop.status_code == 200
    assert stop.json()["ok"] is True
    state = store.load_scan_state()
    assert not state.get("start_requested")
    assert state.get("status") != "queued"
