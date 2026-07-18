"""Local data plane paths (gitignored runtime under analytics/data/)."""

from __future__ import annotations

from pathlib import Path

# src/crawley/data/paths.py → parents[3] = apps/crawley/analytics (uv project root)
ANALYTICS_ROOT = Path(__file__).resolve().parents[3]


def _find_git_root(start: Path) -> Path:
    """Walk up for a git checkout (monorepo root after Phase 4 merge)."""
    for path in (start, *start.parents):
        if (path / ".git").exists():
            return path
    return start


# Git checkout root (Settings → Update). Distinct from ANALYTICS_ROOT when nested.
REPO_ROOT = _find_git_root(ANALYTICS_ROOT)
DATA_DIR = ANALYTICS_ROOT / "data"
SECRETS_DIR = DATA_DIR / "secrets"
INVESTMENT_DIR = DATA_DIR / "investment"
GMAIL_DIR = DATA_DIR / "gmail"
CALENDAR_DIR = DATA_DIR / "calendar"
FITNESS_DIR = DATA_DIR / "fitness"
WORK_DIR = DATA_DIR / "work"
CO_PARENTING_DIR = DATA_DIR / "co_parenting"
DIY_DIR = DATA_DIR / "diy"
FINANCE_DIR = DATA_DIR / "finance"
CODING_DIR = DATA_DIR / "coding_creative"
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
        CO_PARENTING_DIR,
        DIY_DIR,
        FINANCE_DIR,
        CODING_DIR,
    ):
        path.mkdir(parents=True, exist_ok=True)
