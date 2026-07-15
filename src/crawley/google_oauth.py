"""Shared Google OAuth (read-only Gmail + Calendar)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

from crawley.data.paths import SECRETS_DIR, ensure_data_dirs

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.readonly",
]
GMAIL_SCOPE = SCOPES[0]
CALENDAR_SCOPE = SCOPES[1]
# Narrow write scope for Calendar event insert (Sprint 8). Never add Gmail send here.
CALENDAR_EVENTS_SCOPE = "https://www.googleapis.com/auth/calendar.events"
SCOPES_WITH_CALENDAR_WRITE = [*SCOPES, CALENDAR_EVENTS_SCOPE]
ALL_TOKEN_SCOPES = SCOPES_WITH_CALENDAR_WRITE

# Keep the historical Gmail callback path so existing Google Cloud redirect URIs keep working.
OAUTH_REDIRECT_PATH = "/modules/gmail/oauth/callback"
TOKEN_PATH = SECRETS_DIR / "google_token.json"
LEGACY_TOKEN_PATH = SECRETS_DIR / "gmail_token.json"
PENDING_OAUTH_PATH = SECRETS_DIR / "google_oauth_pending.json"
LEGACY_PENDING_PATH = SECRETS_DIR / "gmail_oauth_pending.json"


def _allow_local_http_oauth(request_base: str) -> None:
    """oauthlib blocks http://; localhost PoC requires an explicit allow."""
    base = request_base.lower()
    if base.startswith("https://"):
        return
    if "127.0.0.1" in base or "localhost" in base:
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


def client_config() -> dict[str, Any]:
    client_id = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET", "").strip()
    if not client_id or not client_secret:
        raise RuntimeError(
            "Google OAuth is not configured. Set GOOGLE_CLIENT_ID and "
            "GOOGLE_CLIENT_SECRET in .env (Desktop / installed app credentials). "
            "Enable Gmail API and Google Calendar API."
        )
    return {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://127.0.0.1", "http://localhost"],
        }
    }


def redirect_uri(request_base: str) -> str:
    return request_base.rstrip("/") + OAUTH_REDIRECT_PATH


def _token_candidates() -> list[Path]:
    return [TOKEN_PATH, LEGACY_TOKEN_PATH]


def _pending_path() -> Path:
    if PENDING_OAUTH_PATH.exists():
        return PENDING_OAUTH_PATH
    if LEGACY_PENDING_PATH.exists():
        return LEGACY_PENDING_PATH
    return PENDING_OAUTH_PATH


def _save_pending_oauth(*, state: str, code_verifier: str, redirect: str) -> None:
    ensure_data_dirs()
    PENDING_OAUTH_PATH.write_text(
        json.dumps(
            {
                "state": state,
                "code_verifier": code_verifier,
                "redirect_uri": redirect,
            }
        ),
        encoding="utf-8",
    )


def _load_pending_oauth() -> dict[str, str]:
    path = _pending_path()
    if not path.exists():
        raise RuntimeError(
            "OAuth session expired or missing. Click Connect Google again "
            "(PKCE code verifier must match the start of the flow)."
        )
    data = json.loads(path.read_text(encoding="utf-8"))
    if not data.get("code_verifier") or not data.get("state"):
        raise RuntimeError(
            "OAuth pending file is incomplete. Click Connect Google again."
        )
    return data


def _clear_pending_oauth() -> None:
    for path in (PENDING_OAUTH_PATH, LEGACY_PENDING_PATH):
        if path.exists():
            path.unlink()


def _normalize_scopes(scopes: Any) -> set[str]:
    if not scopes:
        return set()
    return {str(s).rstrip("/") for s in scopes}


def has_scope(creds: Credentials | None, scope: str) -> bool:
    if not creds:
        return False
    granted = _normalize_scopes(getattr(creds, "scopes", None))
    if not granted:
        # Older tokens sometimes omit scopes; treat as Gmail-only legacy.
        return scope.rstrip("/") == GMAIL_SCOPE.rstrip("/")
    return scope.rstrip("/") in granted


def load_credentials() -> Credentials | None:
    ensure_data_dirs()
    path = next((p for p in _token_candidates() if p.exists()), None)
    if path is None:
        return None
    creds = Credentials.from_authorized_user_file(str(path), ALL_TOKEN_SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        save_credentials(creds)
    if creds and creds.valid:
        return creds
    return None


def save_credentials(creds: Credentials) -> None:
    ensure_data_dirs()
    TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")
    # Keep legacy path in sync for older tooling / docs until cutover.
    LEGACY_TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")


def build_auth_flow(
    request_base: str,
    *,
    include_calendar_write: bool = False,
) -> Flow:
    _allow_local_http_oauth(request_base)
    scopes = SCOPES_WITH_CALENDAR_WRITE if include_calendar_write else SCOPES
    flow = Flow.from_client_config(client_config(), scopes=scopes)
    flow.redirect_uri = redirect_uri(request_base)
    return flow


def authorization_url(
    request_base: str,
    *,
    include_calendar_write: bool = False,
) -> tuple[str, str]:
    flow = build_auth_flow(
        request_base, include_calendar_write=include_calendar_write
    )
    url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    verifier = getattr(flow, "code_verifier", None)
    if not verifier:
        raise RuntimeError("OAuth flow did not produce a PKCE code_verifier.")
    _save_pending_oauth(
        state=state,
        code_verifier=verifier,
        redirect=flow.redirect_uri,
    )
    # Remember which scope set was requested for finish_oauth.
    ensure_data_dirs()
    pending = json.loads(PENDING_OAUTH_PATH.read_text(encoding="utf-8"))
    pending["include_calendar_write"] = include_calendar_write
    PENDING_OAUTH_PATH.write_text(json.dumps(pending), encoding="utf-8")
    return url, state


def finish_oauth(request_base: str, authorization_response: str) -> Credentials:
    pending = _load_pending_oauth()
    query = parse_qs(urlparse(authorization_response).query)
    returned_state = (query.get("state") or [None])[0]
    if returned_state != pending["state"]:
        raise RuntimeError("OAuth state mismatch. Click Connect Google again.")

    include_write = bool(pending.get("include_calendar_write"))
    flow = build_auth_flow(request_base, include_calendar_write=include_write)
    flow.redirect_uri = pending.get("redirect_uri") or flow.redirect_uri
    flow.code_verifier = pending["code_verifier"]
    flow.fetch_token(authorization_response=authorization_response)
    creds = flow.credentials
    save_credentials(creds)
    _clear_pending_oauth()
    return creds


def google_auth_status() -> dict[str, Any]:
    """Shared connect state for Gmail, Calendar, and home chips."""
    try:
        client_config()
        client_ok = True
        client_error = None
    except RuntimeError as exc:
        client_ok = False
        client_error = str(exc)
        return {
            "client_ok": False,
            "connected": False,
            "gmail_ok": False,
            "calendar_ok": False,
            "calendar_write_ok": False,
            "needs_reconsent": False,
            "error": client_error,
            "token_path": str(TOKEN_PATH),
        }

    try:
        creds = load_credentials()
    except Exception as exc:  # noqa: BLE001
        return {
            "client_ok": True,
            "connected": False,
            "gmail_ok": False,
            "calendar_ok": False,
            "calendar_write_ok": False,
            "needs_reconsent": False,
            "error": f"Saved token could not be loaded: {exc}",
            "token_path": str(TOKEN_PATH),
        }

    connected = bool(creds and creds.valid)
    gmail_ok = connected and has_scope(creds, GMAIL_SCOPE)
    calendar_ok = connected and has_scope(creds, CALENDAR_SCOPE)
    calendar_write_ok = connected and has_scope(creds, CALENDAR_EVENTS_SCOPE)
    needs_reconsent = connected and (not gmail_ok or not calendar_ok)

    error = None
    if needs_reconsent and not calendar_ok:
        error = (
            "Google is connected for Gmail, but Calendar access is missing. "
            "Reconnect to grant Calendar (read-only)."
        )
    elif needs_reconsent:
        error = "Google token is missing required read-only scopes. Reconnect."

    return {
        "client_ok": client_ok,
        "connected": connected,
        "gmail_ok": gmail_ok,
        "calendar_ok": calendar_ok,
        "calendar_write_ok": calendar_write_ok,
        "needs_reconsent": needs_reconsent,
        "error": error,
        "token_path": str(TOKEN_PATH),
    }
