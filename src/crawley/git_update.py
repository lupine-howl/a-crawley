"""Local git pull for Settings → Update (Sprint 11)."""

from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from crawley.data.paths import REPO_ROOT

_SECRETISH = re.compile(
    r"(?i)(authorization:\s*\S+|token[=:]\s*\S+|api[_-]?key[=:]\s*\S+)"
)


@dataclass(frozen=True)
class GitStatus:
    ok: bool
    is_repo: bool
    branch: str
    short_sha: str
    remote: str
    dirty: bool
    message: str


@dataclass(frozen=True)
class PullResult:
    ok: bool
    state: str  # success | up_to_date | error | blocked_dirty | not_repo
    message: str
    branch: str
    before_sha: str
    after_sha: str
    changed_watched: bool
    reload_enabled: bool
    lan_warn: bool = False


def _run_git(args: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=str(cwd or REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )


def _scrub(text: str) -> str:
    cleaned = _SECRETISH.sub("[redacted]", text or "")
    # Keep short for UI.
    lines = [ln for ln in cleaned.strip().splitlines() if ln.strip()]
    return "\n".join(lines[:12]).strip()


def reload_enabled() -> bool:
    raw = os.environ.get("CRAWLEY_RELOAD", "").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def git_status() -> GitStatus:
    root = REPO_ROOT
    if not (root / ".git").exists() and not (root / ".git").is_file():
        # Worktree .git can be a file; still treat missing git metadata as not a repo.
        probe = _run_git(["rev-parse", "--is-inside-work-tree"])
        if probe.returncode != 0 or probe.stdout.strip() != "true":
            return GitStatus(
                ok=False,
                is_repo=False,
                branch="",
                short_sha="",
                remote="",
                dirty=False,
                message="Not a git checkout — Update is unavailable.",
            )

    branch_p = _run_git(["rev-parse", "--abbrev-ref", "HEAD"])
    sha_p = _run_git(["rev-parse", "--short", "HEAD"])
    remote_p = _run_git(["rev-parse", "--abbrev-ref", "@{upstream}"])
    dirty_p = _run_git(["status", "--porcelain"])

    branch = branch_p.stdout.strip() if branch_p.returncode == 0 else ""
    short_sha = sha_p.stdout.strip() if sha_p.returncode == 0 else ""
    remote = remote_p.stdout.strip() if remote_p.returncode == 0 else ""
    dirty = bool(dirty_p.stdout.strip()) if dirty_p.returncode == 0 else False

    if branch_p.returncode != 0:
        return GitStatus(
            ok=False,
            is_repo=False,
            branch="",
            short_sha="",
            remote="",
            dirty=False,
            message=_scrub(branch_p.stderr) or "Unable to read git branch.",
        )

    msg = f"Branch {branch} · {short_sha}"
    if remote:
        msg += f" · tracking {remote}"
    if dirty:
        msg += " · working tree has local changes"
    return GitStatus(
        ok=True,
        is_repo=True,
        branch=branch,
        short_sha=short_sha,
        remote=remote,
        dirty=dirty,
        message=msg,
    )


def _watched_paths_changed(before: str, after: str) -> bool:
    if not before or not after or before == after:
        return False
    diff = _run_git(["diff", "--name-only", f"{before}..{after}"])
    if diff.returncode != 0:
        return False
    for line in diff.stdout.splitlines():
        path = line.strip().replace("\\", "/")
        if path.startswith("src/crawley/"):
            return True
    return False


def pull_latest(*, lan_bound: bool = False) -> PullResult:
    """
    Fetch + ff-only merge of the current branch's upstream.

    Allowed on localhost and trusted LAN/Tailscale. Does not attempt merge
    conflict resolution (ff-only only).
    """
    status = git_status()
    if not status.is_repo:
        return PullResult(
            ok=False,
            state="not_repo",
            message=status.message,
            branch="",
            before_sha="",
            after_sha="",
            changed_watched=False,
            reload_enabled=reload_enabled(),
            lan_warn=lan_bound,
        )
    if not status.remote:
        return PullResult(
            ok=False,
            state="error",
            message=(
                f"Branch {status.branch!r} has no upstream. "
                "Set upstream (e.g. git push -u origin HEAD) then retry."
            ),
            branch=status.branch,
            before_sha=status.short_sha,
            after_sha=status.short_sha,
            changed_watched=False,
            reload_enabled=reload_enabled(),
            lan_warn=lan_bound,
        )

    before_full = _run_git(["rev-parse", "HEAD"])
    before = before_full.stdout.strip() if before_full.returncode == 0 else ""

    fetch = _run_git(["fetch", "--prune"])
    if fetch.returncode != 0:
        return PullResult(
            ok=False,
            state="error",
            message=_scrub(fetch.stderr) or "git fetch failed.",
            branch=status.branch,
            before_sha=status.short_sha,
            after_sha=status.short_sha,
            changed_watched=False,
            reload_enabled=reload_enabled(),
            lan_warn=lan_bound,
        )

    merge = _run_git(["merge", "--ff-only", "@{upstream}"])
    after_full = _run_git(["rev-parse", "HEAD"])
    after = after_full.stdout.strip() if after_full.returncode == 0 else before
    after_short_p = _run_git(["rev-parse", "--short", "HEAD"])
    after_short = after_short_p.stdout.strip() if after_short_p.returncode == 0 else ""

    if merge.returncode != 0:
        err = _scrub(merge.stderr) or _scrub(merge.stdout) or "git merge --ff-only failed."
        state = "error"
        if "Not possible to fast-forward" in (merge.stderr + merge.stdout):
            err = (
                "Cannot fast-forward — local history diverged from upstream. "
                "Resolve in a terminal (rebase/merge); conflict UI is out of scope."
            )
        return PullResult(
            ok=False,
            state=state,
            message=err,
            branch=status.branch,
            before_sha=status.short_sha,
            after_sha=after_short or status.short_sha,
            changed_watched=False,
            reload_enabled=reload_enabled(),
            lan_warn=lan_bound,
        )

    changed = _watched_paths_changed(before, after)
    if before == after:
        return PullResult(
            ok=True,
            state="up_to_date",
            message=f"Already up to date ({status.branch} · {after_short}).",
            branch=status.branch,
            before_sha=status.short_sha,
            after_sha=after_short,
            changed_watched=False,
            reload_enabled=reload_enabled(),
            lan_warn=lan_bound,
        )

    reload = reload_enabled()
    msg = f"Pulled {status.branch}: {status.short_sha} → {after_short}."
    if changed and reload:
        msg += " Watched files changed — hot reload should apply shortly."
    elif changed and not reload:
        msg += " Watched files changed — set CRAWLEY_RELOAD=1 and restart to auto-reload."
    elif not changed:
        msg += " No changes under src/crawley/ (reload may not fire)."
    if lan_bound:
        msg += " (Trusted LAN/Tailscale — no login gate.)"

    return PullResult(
        ok=True,
        state="success",
        message=msg,
        branch=status.branch,
        before_sha=status.short_sha,
        after_sha=after_short,
        changed_watched=changed,
        reload_enabled=reload,
        lan_warn=lan_bound,
    )
