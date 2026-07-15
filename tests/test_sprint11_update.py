"""Sprint 11 — Settings Update (git pull + hot reload)."""

from __future__ import annotations

from unittest.mock import MagicMock

from fastapi.testclient import TestClient

import crawley.git_update as git_update
from crawley.git_update import GitStatus, PullResult, pull_latest


def test_settings_shows_update_section(client: TestClient) -> None:
    resp = client.get("/settings")
    assert resp.status_code == 200
    assert 'id="update"' in resp.text
    assert "Pull latest" in resp.text
    assert "CRAWLEY_RELOAD" in resp.text


def test_pull_blocked_on_lan(monkeypatch) -> None:
    monkeypatch.setattr(
        git_update,
        "git_status",
        lambda: GitStatus(
            ok=True,
            is_repo=True,
            branch="main",
            short_sha="abc1234",
            remote="origin/main",
            dirty=False,
            message="Branch main · abc1234",
        ),
    )
    result = pull_latest(lan_bound=True)
    assert result.ok is False
    assert result.state == "blocked_lan"


def test_pull_up_to_date(monkeypatch) -> None:
    monkeypatch.setattr(
        git_update,
        "git_status",
        lambda: GitStatus(
            ok=True,
            is_repo=True,
            branch="main",
            short_sha="abc1234",
            remote="origin/main",
            dirty=False,
            message="Branch main · abc1234",
        ),
    )

    def fake_run(args, **kwargs):
        cmd = args[0] if args else ""
        # args is full argv starting with "git"
        full = args
        p = MagicMock()
        p.returncode = 0
        if "fetch" in full:
            p.stdout, p.stderr = "", ""
        elif "merge" in full:
            p.stdout, p.stderr = "Already up to date.\n", ""
        elif full[-1] == "HEAD" and "rev-parse" in full:
            p.stdout, p.stderr = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n", ""
        elif "--short" in full:
            p.stdout, p.stderr = "abc1234\n", ""
        else:
            p.stdout, p.stderr = "", ""
        return p

    monkeypatch.setattr(git_update, "_run_git", fake_run)
    result = pull_latest(lan_bound=False)
    assert result.ok is True
    assert result.state == "up_to_date"


def test_pull_success_detects_watched_change(monkeypatch) -> None:
    monkeypatch.setattr(
        git_update,
        "git_status",
        lambda: GitStatus(
            ok=True,
            is_repo=True,
            branch="main",
            short_sha="aaa1111",
            remote="origin/main",
            dirty=False,
            message="Branch main · aaa1111",
        ),
    )
    monkeypatch.setenv("CRAWLEY_RELOAD", "1")

    shas = {
        "before": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "after": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
    }

    def fake_run(args, **kwargs):
        full = list(args)
        p = MagicMock()
        p.returncode = 0
        p.stderr = ""
        if "fetch" in full:
            p.stdout = ""
        elif "merge" in full:
            p.stdout = "Updating aaa1111..bbb2222\n"
        elif "--short" in full:
            p.stdout = "bbb2222\n"
        elif "diff" in full and "--name-only" in full:
            p.stdout = "src/crawley/shell/routes.py\nREADME.md\n"
        elif "rev-parse" in full and full[-1] == "HEAD":
            # first call before, later after merge
            if not hasattr(fake_run, "n"):
                fake_run.n = 0  # type: ignore[attr-defined]
            fake_run.n += 1  # type: ignore[attr-defined]
            p.stdout = (shas["before"] if fake_run.n == 1 else shas["after"]) + "\n"  # type: ignore[attr-defined]
        else:
            p.stdout = ""
        return p

    monkeypatch.setattr(git_update, "_run_git", fake_run)
    result = pull_latest(lan_bound=False)
    assert result.ok is True
    assert result.state == "success"
    assert result.changed_watched is True
    assert result.reload_enabled is True
    assert "hot reload" in result.message.lower()


def test_pull_route_htmx(client: TestClient, monkeypatch) -> None:
    monkeypatch.setattr(
        "crawley.shell.routes.pull_latest",
        lambda **kwargs: PullResult(
            ok=True,
            state="up_to_date",
            message="Already up to date (main · abc1234).",
            branch="main",
            before_sha="abc1234",
            after_sha="abc1234",
            changed_watched=False,
            reload_enabled=False,
        ),
    )
    resp = client.post(
        "/settings/update/pull",
        headers={"HX-Request": "true"},
    )
    assert resp.status_code == 200
    assert "Already up to date" in resp.text
    assert 'id="update"' in resp.text
