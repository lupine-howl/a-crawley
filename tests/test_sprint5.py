"""Sprint 5: LAN settings, Work module, write-back dry-run."""

from __future__ import annotations

from fastapi.testclient import TestClient

from crawley.bind import (
    host_exposes_lan,
    is_tailscale_host,
    is_trusted_personal_host,
    resolve_bind_host,
)
from crawley.data.snapshots import save_snapshot
from crawley.llm.base import ChatResult
from crawley.modules.registry import build_registry
from crawley.settings import load_settings, update_network_settings


def test_default_bind_is_localhost(monkeypatch) -> None:
    monkeypatch.delenv("CRAWLEY_HOST", raising=False)
    update_network_settings(lan_enabled=False)
    assert resolve_bind_host() == "127.0.0.1"
    assert not host_exposes_lan(resolve_bind_host())


def test_lan_setting_resolves_to_all_interfaces(monkeypatch) -> None:
    monkeypatch.delenv("CRAWLEY_HOST", raising=False)
    update_network_settings(lan_enabled=True)
    assert resolve_bind_host() == "0.0.0.0"
    assert host_exposes_lan("0.0.0.0")


def test_env_host_overrides_settings(monkeypatch) -> None:
    update_network_settings(lan_enabled=False)
    monkeypatch.setenv("CRAWLEY_HOST", "0.0.0.0")
    assert resolve_bind_host() == "0.0.0.0"


def test_tailscale_and_trusted_personal_hosts() -> None:
    assert is_tailscale_host("100.64.1.2")
    assert is_tailscale_host("host.tailscale.net")
    assert is_tailscale_host("machine.ts.net")
    assert not is_tailscale_host("192.168.1.10")
    assert is_trusted_personal_host("100.101.0.5")
    assert is_trusted_personal_host("192.168.1.10")
    assert is_trusted_personal_host("127.0.0.1")
    assert not is_trusted_personal_host("8.8.8.8")


def test_settings_network_toggle(client: TestClient) -> None:
    response = client.post(
        "/settings/network",
        data={"lan_enabled": "on"},
        headers={"HX-Request": "true"},
    )
    assert response.status_code == 200
    assert "Restart" in response.text or "restart" in response.text.lower()
    assert load_settings().network.lan_enabled is True
    assert "Trusted" in response.text or "trusted" in response.text.lower() or "LAN" in response.text


def test_work_leaves_coming_soon(client: TestClient) -> None:
    page = client.get("/modules/work")
    assert page.status_code == 200
    assert "Coming soon" not in page.text
    assert "Prioritize" in page.text


def test_work_save_and_prioritize(client: TestClient, monkeypatch) -> None:
    class FakeProvider:
        def complete(self, messages, *, max_tokens=512):
            return ChatResult(content="## Top priorities\n- Ship Sprint 5", model="fake")

    monkeypatch.setattr(
        "crawley.modules.work.get_llm_provider",
        lambda: FakeProvider(),
    )
    save = client.post(
        "/modules/work/save",
        data={"notes": "- A\n- B"},
        headers={"HX-Request": "true"},
    )
    assert save.status_code == 200
    assert "saved" in save.text.lower() or "Notes saved" in save.text

    module = client.app.state.registry["work"]
    module._job_body("- A\n- B")
    assert module.job.status == "done"
    assert "Ship Sprint 5" in module.job.summary
    home = client.get("/")
    assert "Last Work" in home.text
    assert "Ship Sprint 5" in home.text


def test_write_back_gmail_propose_cancel(client: TestClient, tmp_path, monkeypatch) -> None:
    import crawley.modules.gmail as gmail_mod
    import crawley.writeback as wb

    monkeypatch.setattr(wb, "AUDIT_PATH", tmp_path / "audit.jsonl")
    monkeypatch.setattr(wb, "DATA_DIR", tmp_path)
    monkeypatch.setattr(gmail_mod, "SEND_DRAFTS_PATH", tmp_path / "pending_send_drafts.json")
    monkeypatch.setattr(gmail_mod, "GMAIL_DIR", tmp_path)
    registry = build_registry()
    gmail = registry["gmail"]
    result = gmail.write_back(
        {
            "action": "propose",
            "to": "a@example.com",
            "subject": "Hi",
            "body": "Hello there",
        }
    )
    assert result.error is None
    draft_id = result.details["draft"]["draft_id"]
    cancelled = gmail.write_back({"action": "cancel", "draft_id": draft_id})
    assert cancelled.error is None
    assert (tmp_path / "audit.jsonl").exists()
    work = registry["work"]
    denied = work.write_back({"action": "x"})
    assert denied.error


def test_home_glance_includes_work_slot(client: TestClient) -> None:
    save_snapshot("work", "## Focus\nShip it")
    home = client.get("/")
    assert "Last Work" in home.text
    assert "Focus" in home.text or "Ship" in home.text
