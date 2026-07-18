"""Thin Google OAuth HTTP surface for crawley-ui deep-links.

Paths are stable (Google Cloud redirect URI + presentation contract):
  GET /modules/gmail/oauth/start
  GET /modules/gmail/oauth/callback

No Jinja product UI — callback returns a minimal HTML page.
"""

from __future__ import annotations

import os
from html import escape

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from crawley.google_oauth import authorization_url, finish_oauth

router = APIRouter(tags=["oauth"])


def _base_url(request: Request) -> str:
    return str(request.base_url).rstrip("/")


def _ui_return_hint() -> str:
    origin = (os.environ.get("CRAWLEY_UI_ORIGIN") or "").strip().rstrip("/")
    if origin:
        return (
            f'<p><a href="{escape(origin)}">Return to crawley-ui</a></p>'
        )
    return (
        "<p>Return to <strong>crawley-ui</strong> "
        "(Sender Inbox → Connect Google is complete).</p>"
    )


def _done_page(*, title: str, body: str, ok: bool) -> HTMLResponse:
    color = "#0a7" if ok else "#b00"
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{escape(title)}</title>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 36rem; margin: 3rem auto; padding: 0 1rem; line-height: 1.5; }}
    h1 {{ color: {color}; font-size: 1.25rem; }}
  </style>
</head>
<body>
  <h1>{escape(title)}</h1>
  <p>{escape(body)}</p>
  {_ui_return_hint()}
  <p style="color:#666;font-size:0.9rem">Crawley analytics — product UI is crawley-ui, not this page.</p>
</body>
</html>
"""
    return HTMLResponse(html, status_code=200 if ok else 400)


@router.get("/modules/gmail/oauth/start", response_model=None)
def gmail_oauth_start(request: Request) -> RedirectResponse | HTMLResponse:
    include_cal = request.query_params.get("calendar_write") == "1"
    include_send = request.query_params.get("gmail_send") == "1"
    include_modify = request.query_params.get("gmail_modify") == "1"
    try:
        url, _state = authorization_url(
            _base_url(request),
            include_calendar_write=include_cal,
            include_gmail_send=include_send,
            include_gmail_modify=include_modify,
        )
        return RedirectResponse(url)
    except Exception as exc:  # noqa: BLE001
        return _done_page(
            title="Google connect failed",
            body=str(exc),
            ok=False,
        )


@router.get("/modules/gmail/oauth/callback", response_model=None)
def gmail_oauth_callback(request: Request) -> HTMLResponse:
    try:
        finish_oauth(_base_url(request), str(request.url))
        return _done_page(
            title="Google connected",
            body=(
                "Gmail credentials saved on the analytics host. "
                "You can close this tab and return to crawley-ui."
            ),
            ok=True,
        )
    except Exception as exc:  # noqa: BLE001
        return _done_page(
            title="OAuth failed",
            body=str(exc),
            ok=False,
        )
