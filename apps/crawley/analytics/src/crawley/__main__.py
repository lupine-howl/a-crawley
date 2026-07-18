"""CLI entry: start the local Crawley server."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
import uvicorn

from crawley.bind import (
    guess_reachable_urls,
    host_exposes_lan,
    resolve_bind_host,
    resolve_bind_port,
)

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src" / "crawley"


def _env_flag(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name, "").strip().lower()
    if not raw:
        return default
    return raw in {"1", "true", "yes", "on"}


def main() -> None:
    load_dotenv(ROOT / ".env")
    host = resolve_bind_host()
    port = resolve_bind_port()
    reload_enabled = _env_flag("CRAWLEY_RELOAD", default=False)
    if host_exposes_lan(host):
        print(
            f"WARNING: Crawley is binding to {host}:{port} (LAN/Tailscale reachable). "
            "Trusted network only — no authentication. "
            "Disable LAN in Settings or set CRAWLEY_HOST=127.0.0.1 and restart."
        )
        print(f"Local URL:     http://127.0.0.1:{port}")
        for url in guess_reachable_urls(port):
            print(f"Try also:      {url}")
        print(
            "Tailscale: use this machine’s Tailscale IP or MagicDNS name + "
            f"port {port}. Prefer Tailscale inside the same WSL/Linux host as Crawley."
        )
    else:
        print(f"Crawley listening on http://{host}:{port} (localhost only).")
    if reload_enabled:
        print(f"Hot reload ON — watching {SRC_DIR} (set CRAWLEY_RELOAD=0 to disable).")
    uvicorn.run(
        "crawley.app:create_app",
        factory=True,
        host=host,
        port=port,
        reload=reload_enabled,
        reload_dirs=[str(SRC_DIR)] if reload_enabled else None,
    )


if __name__ == "__main__":
    main()
