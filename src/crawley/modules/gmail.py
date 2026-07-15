"""Gmail read-only OAuth + bounded inbox skim."""

from __future__ import annotations

import json
import logging
import os
from datetime import UTC, datetime
from email.utils import parseaddr
from typing import Any
from urllib.parse import parse_qs, urlparse

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from crawley.data.duck import duck_connection
from crawley.data.paths import GMAIL_DIR, SECRETS_DIR, ensure_data_dirs
from crawley.jobs import JobState
from crawley.llm.base import ChatMessage, LLMError
from crawley.llm.factory import get_llm_provider
from crawley.modules.contract import Module, ModuleKind, ModuleMeta, ModuleOutput
from crawley.prompts import build_gmail_user_message
from crawley.settings import load_settings

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
TOKEN_PATH = SECRETS_DIR / "gmail_token.json"
PENDING_OAUTH_PATH = SECRETS_DIR / "gmail_oauth_pending.json"
MAX_MESSAGES = 8
OAUTH_REDIRECT_PATH = "/modules/gmail/oauth/callback"


def _allow_local_http_oauth(request_base: str) -> None:
    """oauthlib blocks http://; localhost PoC requires an explicit allow."""
    base = request_base.lower()
    if base.startswith("https://"):
        return
    if "127.0.0.1" in base or "localhost" in base:
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


def _client_config() -> dict[str, Any]:
    client_id = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET", "").strip()
    if not client_id or not client_secret:
        raise RuntimeError(
            "Google OAuth is not configured. Set GOOGLE_CLIENT_ID and "
            "GOOGLE_CLIENT_SECRET in .env (Desktop / installed app credentials)."
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
    if not PENDING_OAUTH_PATH.exists():
        raise RuntimeError(
            "OAuth session expired or missing. Click Connect Gmail again "
            "(PKCE code verifier must match the start of the flow)."
        )
    data = json.loads(PENDING_OAUTH_PATH.read_text(encoding="utf-8"))
    if not data.get("code_verifier") or not data.get("state"):
        raise RuntimeError(
            "OAuth pending file is incomplete. Click Connect Gmail again."
        )
    return data


def _clear_pending_oauth() -> None:
    if PENDING_OAUTH_PATH.exists():
        PENDING_OAUTH_PATH.unlink()


def load_credentials() -> Credentials | None:
    ensure_data_dirs()
    if not TOKEN_PATH.exists():
        return None
    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")
    if creds and creds.valid:
        return creds
    return None


def save_credentials(creds: Credentials) -> None:
    ensure_data_dirs()
    TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")


def build_auth_flow(request_base: str) -> Flow:
    _allow_local_http_oauth(request_base)
    flow = Flow.from_client_config(_client_config(), scopes=SCOPES)
    flow.redirect_uri = redirect_uri(request_base)
    return flow


def authorization_url(request_base: str) -> tuple[str, str]:
    flow = build_auth_flow(request_base)
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
    return url, state


def finish_oauth(request_base: str, authorization_response: str) -> Credentials:
    pending = _load_pending_oauth()
    query = parse_qs(urlparse(authorization_response).query)
    returned_state = (query.get("state") or [None])[0]
    if returned_state != pending["state"]:
        raise RuntimeError("OAuth state mismatch. Click Connect Gmail again.")

    flow = build_auth_flow(request_base)
    flow.redirect_uri = pending.get("redirect_uri") or flow.redirect_uri
    flow.code_verifier = pending["code_verifier"]
    flow.fetch_token(authorization_response=authorization_response)
    creds = flow.credentials
    save_credentials(creds)
    _clear_pending_oauth()
    return creds


def _header_map(payload_headers: list[dict[str, str]]) -> dict[str, str]:
    return {h.get("name", "").lower(): h.get("value", "") for h in payload_headers}


def fetch_inbox_skim(creds: Credentials, *, limit: int = MAX_MESSAGES) -> list[dict[str, str]]:
    service = build("gmail", "v1", credentials=creds, cache_discovery=False)
    listed = (
        service.users()
        .messages()
        .list(userId="me", labelIds=["INBOX"], maxResults=limit)
        .execute()
    )
    messages = listed.get("messages", [])
    rows: list[dict[str, str]] = []
    now = datetime.now(UTC).replace(tzinfo=None)
    ensure_data_dirs()
    cache_dir = GMAIL_DIR / datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    cache_dir.mkdir(parents=True, exist_ok=True)

    with duck_connection() as con:
        for meta in messages:
            msg_id = meta["id"]
            full = (
                service.users()
                .messages()
                .get(userId="me", id=msg_id, format="metadata", metadataHeaders=["From", "Subject", "Date"])
                .execute()
            )
            headers = _header_map(full.get("payload", {}).get("headers", []))
            subject = headers.get("subject", "(no subject)")
            from_addr = parseaddr(headers.get("from", ""))[1] or headers.get("from", "")
            snippet = full.get("snippet", "")
            internal_ms = int(full.get("internalDate", "0"))
            internal_dt = (
                datetime.fromtimestamp(internal_ms / 1000, tz=UTC).replace(tzinfo=None)
                if internal_ms
                else now
            )
            (cache_dir / f"{msg_id}.txt").write_text(
                f"From: {from_addr}\nSubject: {subject}\n\n{snippet}\n",
                encoding="utf-8",
            )
            con.execute(
                """
                INSERT OR REPLACE INTO gmail_messages
                (id, fetched_at, internal_date, subject, from_addr, snippet)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                [msg_id, now, internal_dt, subject, from_addr, snippet[:500]],
            )
            rows.append(
                {
                    "id": msg_id,
                    "subject": subject,
                    "from": from_addr,
                    "snippet": snippet[:400],
                }
            )
    return rows


class GmailModule(Module):
    meta = ModuleMeta(
        id="gmail",
        title="Gmail",
        kind=ModuleKind.LIVE,
        nav_order=20,
        description="Read-only inbox skim and summary (lite PoC).",
    )

    def __init__(self) -> None:
        self.job = JobState(
            status="idle",
            message="Connect Gmail (read-only), then run a bounded inbox skim.",
        )
        self._executor = None
        self.oauth_state: str | None = None

    def bind_executor(self, executor) -> None:
        self._executor = executor

    def auth_status(self) -> dict[str, Any]:
        try:
            _client_config()
            client_ok = True
            client_error = None
        except RuntimeError as exc:
            client_ok = False
            client_error = str(exc)

        creds = None
        if client_ok:
            try:
                creds = load_credentials()
            except Exception as exc:  # noqa: BLE001
                return {
                    "client_ok": True,
                    "connected": False,
                    "error": f"Saved token could not be loaded: {exc}",
                }

        return {
            "client_ok": client_ok,
            "connected": bool(creds and creds.valid),
            "error": client_error,
            "token_path": str(TOKEN_PATH),
        }

    def panel_context(self) -> dict[str, Any]:
        return {
            "coming_soon": False,
            "description": self.meta.description,
            "job": self.job.to_dict(),
            "auth": self.auth_status(),
            "max_messages": MAX_MESSAGES,
        }

    def run(self, inputs: dict[str, Any] | None = None) -> ModuleOutput:
        if self.job.status == "busy":
            return ModuleOutput(error="Gmail job already running.")
        if self._executor is None:
            return ModuleOutput(error="Executor not configured.")

        auth = self.auth_status()
        if not auth["client_ok"]:
            self.job = JobState(status="error", message=auth["error"] or "OAuth not configured.")
            return ModuleOutput(error=self.job.message)
        if not auth["connected"]:
            self.job = JobState(
                status="error",
                message="Gmail is not connected. Use Connect Gmail first.",
            )
            return ModuleOutput(error=self.job.message)

        self.job = JobState(status="busy", message="Scanning inbox…")
        self._executor.submit(self._job_body)
        return ModuleOutput(summary="started", details={"status": "busy"})

    def _job_body(self) -> None:
        try:
            creds = load_credentials()
            if not creds:
                self.job = JobState(
                    status="error",
                    message="Gmail token missing or invalid. Reconnect Gmail.",
                )
                return
            self.job = JobState(status="busy", message="Fetching recent inbox messages…")
            rows = fetch_inbox_skim(creds)
            if not rows:
                self.job = JobState(
                    status="done",
                    message="Inbox scan returned no messages.",
                    summary="No recent inbox messages found.",
                )
                return

            self.job = JobState(status="busy", message="Summarizing with LLM…")
            lines = [
                f"- From {r['from']}: {r['subject']} — {r['snippet'][:200]}" for r in rows
            ]
            prompts = load_settings().prompts
            system = prompts.gmail_system
            user = build_gmail_user_message(
                header=prompts.gmail_user_header,
                inbox_lines=lines,
            )
            provider = get_llm_provider()
            result = provider.complete(
                [
                    ChatMessage(role="system", content=system),
                    ChatMessage(role="user", content=user),
                ],
                max_tokens=350,
            )
            self.job = JobState(
                status="done",
                message=f"Done — skimmed {len(rows)} messages.",
                summary=result.content,
                details={
                    "count": len(rows),
                    "model": result.model,
                    "prompt_system": system,
                    "prompt_user": user,
                },
            )
            try:
                from crawley.data.snapshots import save_snapshot

                save_snapshot("gmail", result.content)
            except Exception:  # noqa: BLE001
                logger.exception("Failed to persist gmail snapshot")
        except HttpError as exc:
            self.job = JobState(
                status="error",
                message=f"Gmail API error: {exc.reason or exc}",
            )
        except LLMError as exc:
            self.job = JobState(status="error", message=str(exc))
        except Exception as exc:  # noqa: BLE001
            logger.exception("Gmail job failed")
            self.job = JobState(status="error", message=f"Gmail run failed: {exc}")
