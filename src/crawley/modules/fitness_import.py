"""Fitness activity import lite (Sprint 16)."""

from __future__ import annotations

from pathlib import Path

from crawley.data.paths import ensure_data_dirs

MAX_IMPORT_BYTES = 64_000


def import_path() -> Path:
    from crawley.data.paths import FITNESS_DIR

    ensure_data_dirs()
    return FITNESS_DIR / "activity_import.txt"


def load_activity_import() -> str:
    path = import_path()
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace").strip()


def clear_activity_import() -> None:
    path = import_path()
    if path.exists():
        path.unlink()


def save_activity_import(raw: bytes | str, *, filename: str = "") -> tuple[bool, str]:
    """Persist a bounded activity artifact. Accepts text/CSV-ish content."""
    ensure_data_dirs()
    if isinstance(raw, str):
        data = raw.encode("utf-8")
    else:
        data = raw
    if not data:
        return False, "Empty file."
    if len(data) > MAX_IMPORT_BYTES:
        return False, f"File too large (max {MAX_IMPORT_BYTES} bytes)."
    if b"\x00" in data[:1000]:
        return False, "Binary files are not supported — use CSV or plain text."
    text = data.decode("utf-8", errors="replace").strip()
    if not text:
        return False, "No readable text in file."
    header = f"# imported {filename or 'activity'}\n" if filename else ""
    import_path().write_text(header + text + "\n", encoding="utf-8")
    return True, f"Imported {len(text)} characters."
