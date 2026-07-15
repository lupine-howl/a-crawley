"""Sprint 3–4: Calendar, Fitness, Investment cache, home glance."""

from __future__ import annotations

from fastapi.testclient import TestClient

from crawley.data.snapshots import save_snapshot
from crawley.llm.base import ChatResult
from crawley.modules.investment_fetch import (
    load_cached_items,
    save_cached_items,
)


def test_investment_query_cache(tmp_path, monkeypatch) -> None:
    import crawley.modules.investment_fetch as inv

    monkeypatch.setattr(inv, "INVESTMENT_DIR", tmp_path)
    items = [
        {
            "title": "T",
            "url": "https://example.com",
            "snippet": "s",
            "published": "",
            "publisher": "X",
        }
    ]
    save_cached_items("markets", items)
    hit = load_cached_items("markets")
    assert hit is not None
    cached, _when = hit
    assert cached[0]["title"] == "T"


def test_calendar_panel_live(client: TestClient) -> None:
    page = client.get("/modules/calendar")
    assert page.status_code == 200
    assert "Coming soon" not in page.text
    assert "Calendar" in page.text


def test_calendar_job_with_mock_events(client: TestClient, monkeypatch) -> None:
    class FakeProvider:
        def complete(self, messages, *, max_tokens=512):
            return ChatResult(content="## Week ahead\nBusy Tuesday.", model="fake")

    monkeypatch.setattr(
        "crawley.modules.calendar.load_credentials",
        lambda: object(),
    )
    monkeypatch.setattr(
        "crawley.modules.calendar.google_auth_status",
        lambda: {
            "client_ok": True,
            "connected": True,
            "gmail_ok": True,
            "calendar_ok": True,
            "needs_reconsent": False,
            "error": None,
            "token_path": "x",
        },
    )
    monkeypatch.setattr(
        "crawley.modules.calendar.CalendarModule.auth_status",
        lambda self: {
            "client_ok": True,
            "connected": True,
            "gmail_ok": True,
            "calendar_ok": True,
            "needs_reconsent": False,
            "error": None,
            "token_path": "x",
        },
    )
    monkeypatch.setattr(
        "crawley.modules.calendar.fetch_upcoming_events",
        lambda creds, days=7, limit=12: [
            {
                "id": "1",
                "title": "Standup",
                "start": "2026-07-16T09:00:00Z",
                "end": "2026-07-16T09:30:00Z",
                "location": "",
                "description": "",
            }
        ],
    )
    monkeypatch.setattr(
        "crawley.modules.calendar.get_llm_provider",
        lambda: FakeProvider(),
    )
    module = client.app.state.registry["calendar"]
    module._job_body()
    assert module.job.status == "done"
    assert "Busy Tuesday" in module.job.summary
    home = client.get("/")
    assert "Busy Tuesday" in home.text or "Week ahead" in home.text


def test_fitness_job_and_disclaimer(client: TestClient, monkeypatch) -> None:
    class FakeProvider:
        def complete(self, messages, *, max_tokens=512):
            return ChatResult(content="## Habits\n- Walk daily", model="fake")

    monkeypatch.setattr(
        "crawley.modules.fitness.get_llm_provider",
        lambda: FakeProvider(),
    )
    page = client.get("/modules/fitness")
    assert "Not medical" in page.text or "not medical" in page.text.lower()

    module = client.app.state.registry["fitness"]
    module._job_body("Walk more this month")
    assert module.job.status == "done"
    assert "Walk daily" in module.job.summary
    home = client.get("/")
    assert "Last Fitness" in home.text
    assert "Walk daily" in home.text


def test_home_glance_shows_all_live_slots(client: TestClient) -> None:
    save_snapshot("investment", "## Inv")
    save_snapshot("gmail", "## Mail")
    save_snapshot("calendar", "## Cal")
    save_snapshot("fitness", "## Fit")
    home = client.get("/")
    assert "Last Investment" in home.text
    assert "Last Gmail" in home.text
    assert "Last Calendar" in home.text
    assert "Last Fitness" in home.text
    assert "Inv" in home.text
    assert "Fit" in home.text
