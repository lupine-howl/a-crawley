"""Bind host/port resolution for the local Crawley server."""

from __future__ import annotations

import ipaddress
import os
import socket

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


def is_loopback_host(host: str) -> bool:
    h = (host or "").strip().lower().rstrip(".")
    return h in {"127.0.0.1", "localhost", "::1"}


def is_tailscale_host(host: str) -> bool:
    """Tailscale MagicDNS or CGNAT (100.64.0.0/10)."""
    h = (host or "").strip().lower().rstrip(".")
    if h.endswith(".ts.net") or h.endswith(".tailscale.net"):
        return True
    try:
        ip = ipaddress.ip_address(h)
    except ValueError:
        return False
    return ip in ipaddress.ip_network("100.64.0.0/10")


def is_trusted_personal_host(host: str) -> bool:
    """Loopback, Tailscale, or private LAN hosts for personal PoC access."""
    h = (host or "").strip().lower().rstrip(".")
    if is_loopback_host(h) or is_tailscale_host(h):
        return True
    try:
        ip = ipaddress.ip_address(h)
    except ValueError:
        return False
    return bool(ip.is_private or ip.is_loopback)


def guess_reachable_urls(port: int) -> list[str]:
    """Best-effort URLs to try from another device (LAN / Tailscale)."""
    urls: list[str] = []
    seen: set[str] = set()

    def add(host: str) -> None:
        host = host.strip().rstrip(".")
        if not host or host in seen:
            return
        seen.add(host)
        urls.append(f"http://{host}:{port}")

    try:
        hostname = socket.gethostname()
        add(hostname)
        for info in socket.getaddrinfo(hostname, None, family=socket.AF_INET):
            add(info[4][0])
    except OSError:
        pass

    # Prefer Tailscale / private addresses first in messaging.
    def sort_key(url: str) -> tuple[int, str]:
        host = urlparse_host(url)
        if is_tailscale_host(host):
            return (0, url)
        if is_trusted_personal_host(host) and not is_loopback_host(host):
            return (1, url)
        return (2, url)

    urls.sort(key=sort_key)
    return urls[:6]


def urlparse_host(url: str) -> str:
    from urllib.parse import urlparse

    return (urlparse(url).hostname or "").lower()
