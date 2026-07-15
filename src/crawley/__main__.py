"""CLI entry: start the local Crawley server."""

from __future__ import annotations

import os

import uvicorn


def main() -> None:
    host = os.environ.get("CRAWLEY_HOST", "127.0.0.1")
    port = int(os.environ.get("CRAWLEY_PORT", "8000"))
    uvicorn.run(
        "crawley.app:create_app",
        factory=True,
        host=host,
        port=port,
        reload=False,
    )


if __name__ == "__main__":
    main()
