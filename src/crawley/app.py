"""FastAPI application factory."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import HTMLResponse


def create_app() -> FastAPI:
    app = FastAPI(title="Crawley", version="0.1.0")

    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Crawley</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 40rem; margin: 3rem auto; padding: 0 1rem; }
    h1 { font-size: 1.75rem; margin-bottom: 0.25rem; }
    p { color: #444; line-height: 1.5; }
  </style>
</head>
<body>
  <h1>Crawley</h1>
  <p>Local shell is running. Dashboard modules land in the next sprint stories.</p>
</body>
</html>
"""

    return app
