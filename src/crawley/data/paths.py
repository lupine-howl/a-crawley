"""Local data plane paths (gitignored runtime under data/)."""

from __future__ import annotations

from pathlib import Path

# src/crawley/data/paths.py → parents[3] = repo root
REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_ROOT / "data"
SECRETS_DIR = DATA_DIR / "secrets"
INVESTMENT_DIR = DATA_DIR / "investment"
GMAIL_DIR = DATA_DIR / "gmail"
CALENDAR_DIR = DATA_DIR / "calendar"
FITNESS_DIR = DATA_DIR / "fitness"
WORK_DIR = DATA_DIR / "work"
DUCKDB_PATH = DATA_DIR / "crawley.duckdb"


def ensure_data_dirs() -> None:
    for path in (
        DATA_DIR,
        SECRETS_DIR,
        INVESTMENT_DIR,
        GMAIL_DIR,
        CALENDAR_DIR,
        FITNESS_DIR,
        WORK_DIR,
    ):
        path.mkdir(parents=True, exist_ok=True)
