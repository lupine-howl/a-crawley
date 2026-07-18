"""Google OAuth PKCE persistence tests."""

from __future__ import annotations

import json

import pytest

import crawley.google_oauth as google_oauth


def test_authorization_url_persists_pkce(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    pending = tmp_path / "pending.json"
    monkeypatch.setattr(google_oauth, "PENDING_OAUTH_PATH", pending)
    monkeypatch.setattr(google_oauth, "SECRETS_DIR", tmp_path)
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "cid.apps.googleusercontent.com")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "csecret")

    class FakeFlow:
        redirect_uri = "http://127.0.0.1:8000/modules/gmail/oauth/callback"
        code_verifier = None

        def authorization_url(self, **kwargs):
            self.code_verifier = "verifier-abc"
            return "https://accounts.google.com/o/oauth2/auth?x=1", "state-xyz"

    monkeypatch.setattr(
        google_oauth, "build_auth_flow", lambda base, **kwargs: FakeFlow()
    )
    url, state = google_oauth.authorization_url("http://127.0.0.1:8000")
    assert "accounts.google.com" in url
    assert state == "state-xyz"
    saved = json.loads(pending.read_text(encoding="utf-8"))
    assert saved["code_verifier"] == "verifier-abc"
    assert saved["state"] == "state-xyz"
    assert saved.get("include_calendar_write") is False


def test_finish_oauth_requires_saved_verifier(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    pending = tmp_path / "pending.json"
    monkeypatch.setattr(google_oauth, "PENDING_OAUTH_PATH", pending)
    monkeypatch.setattr(google_oauth, "LEGACY_PENDING_PATH", tmp_path / "legacy.json")
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "cid.apps.googleusercontent.com")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "csecret")

    with pytest.raises(RuntimeError, match="missing"):
        google_oauth.finish_oauth(
            "http://127.0.0.1:8000",
            "http://127.0.0.1:8000/modules/gmail/oauth/callback?code=x&state=s",
        )


def test_finish_oauth_restores_verifier(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    pending = tmp_path / "pending.json"
    token = tmp_path / "google_token.json"
    legacy = tmp_path / "gmail_token.json"
    monkeypatch.setattr(google_oauth, "PENDING_OAUTH_PATH", pending)
    monkeypatch.setattr(google_oauth, "TOKEN_PATH", token)
    monkeypatch.setattr(google_oauth, "LEGACY_TOKEN_PATH", legacy)
    monkeypatch.setattr(google_oauth, "SECRETS_DIR", tmp_path)
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "cid.apps.googleusercontent.com")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "csecret")

    pending.write_text(
        json.dumps(
            {
                "state": "state-xyz",
                "code_verifier": "verifier-abc",
                "redirect_uri": "http://127.0.0.1:8000/modules/gmail/oauth/callback",
            }
        ),
        encoding="utf-8",
    )

    class FakeCreds:
        def to_json(self) -> str:
            return '{"token":"t"}'

    class FakeFlow:
        redirect_uri = ""
        code_verifier = None
        credentials = FakeCreds()

        def fetch_token(self, authorization_response: str) -> None:
            assert self.code_verifier == "verifier-abc"
            assert "code=abc" in authorization_response

    monkeypatch.setattr(
        google_oauth, "build_auth_flow", lambda base, **kwargs: FakeFlow()
    )
    creds = google_oauth.finish_oauth(
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8000/modules/gmail/oauth/callback?code=abc&state=state-xyz",
    )
    assert isinstance(creds, FakeCreds)
    assert token.exists()
    assert legacy.exists()
    assert not pending.exists()


def test_scopes_include_gmail_and_calendar() -> None:
    assert "gmail.readonly" in google_oauth.SCOPES[0]
    assert "calendar.readonly" in google_oauth.SCOPES[1]
    assert "calendar.events" in google_oauth.CALENDAR_EVENTS_SCOPE
    assert google_oauth.CALENDAR_EVENTS_SCOPE in google_oauth.SCOPES_WITH_CALENDAR_WRITE
