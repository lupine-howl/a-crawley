"""Bind host/port resolution for the local Crawley server."""

from __future__ import annotations

import os

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
LAN_HOST = "0.0.0.0"


def resolve_bind_host(*, lan_enabled: bool | None = None) -> str:
    """
    Resolve listen host.

    Precedence:
    1. Non-empty ``CRAWLEY_HOST`` environment variable (always wins)
    2. Settings ``network.lan_enabled`` → ``0.0.0.0``
    3. Default ``127.0.0.1``
    """
    env = os.environ.get("CRAWLEY_HOST", "").strip()
    if env:
        return env
    if lan_enabled is None:
        from crawley.settings import load_settings

        lan_enabled = load_settings().network.lan_enabled
    return LAN_HOST if lan_enabled else DEFAULT_HOST


def resolve_bind_port() -> int:
    raw = os.environ.get("CRAWLEY_PORT", str(DEFAULT_PORT)).strip()
    try:
        return int(raw)
    except ValueError:
        return DEFAULT_PORT


def host_exposes_lan(host: str) -> bool:
    """True when the process is not bound to loopback-only."""
    h = (host or "").strip().lower()
    return h not in {"127.0.0.1", "localhost", "::1", ""}
