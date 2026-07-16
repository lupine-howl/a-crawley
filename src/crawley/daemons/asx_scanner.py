"""ASX scanner daemon — owns the scan loop outside the API process.

Usage:

    # One-shot (run until complete / paused)
    uv run python -m crawley.daemons.asx_scanner once --force

    # Watch for API-queued starts (set CRAWLEY_ASX_WORKER=daemon on the API)
    uv run python -m crawley.daemons.asx_scanner watch

    # Print disk job status
    uv run python -m crawley.daemons.asx_scanner status

Also installed as console script: ``crawley-asx-scanner``.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3]


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s [asx-scanner] %(message)s",
        datefmt="%H:%M:%S",
    )


def cmd_status() -> int:
    from crawley.api.presentation import present_asx_scan_job
    from crawley.asx_desk.worker import external_worker_mode

    job = present_asx_scan_job()
    payload = job.model_dump()
    payload["worker_mode"] = "daemon" if external_worker_mode() else "in_process"
    print(json.dumps(payload, indent=2))
    return 0


def cmd_once(*, force: bool) -> int:
    from crawley.asx_desk.worker import run_scan_in_this_process

    ok, msg = run_scan_in_this_process(force=force)
    print(msg)
    return 0 if ok else 1


def cmd_watch(*, poll_s: float, force_default: bool) -> int:
    """Poll scan_state for API-queued starts and run them in this process."""
    from crawley.asx_desk.worker import claim_queued_scan, run_scan_in_this_process

    logging.info(
        "Watching for queued scans (poll=%.1fs). "
        "API should set CRAWLEY_ASX_WORKER=daemon.",
        poll_s,
    )
    while True:
        if claim_queued_scan():
            logging.info("Claiming queued scan…")
            ok, msg = run_scan_in_this_process(force=force_default)
            logging.info("%s", msg)
            if not ok:
                time.sleep(poll_s)
                continue
        time.sleep(poll_s)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crawley-asx-scanner",
        description="Crawley ASX desk scanner daemon (threads OK; no Celery).",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    sub = parser.add_subparsers(dest="command", required=True)

    once = sub.add_parser("once", help="Run one scan to completion in this process")
    once.add_argument(
        "--force",
        action="store_true",
        help="Clear active-set progress and re-run even if already complete",
    )

    watch = sub.add_parser(
        "watch",
        help="Loop: claim start_requested from API (CRAWLEY_ASX_WORKER=daemon)",
    )
    watch.add_argument("--poll", type=float, default=1.0, help="Poll interval seconds")
    watch.add_argument(
        "--force",
        action="store_true",
        help="Default force when claiming a queue that did not set force_requested",
    )

    sub.add_parser("status", help="Print /v1-shaped job status from disk")
    return parser


def main(argv: list[str] | None = None) -> int:
    load_dotenv(ROOT / ".env")
    # Ensure data dirs exist for a headless daemon (same as API startup).
    from crawley.data.duck import init_schema
    from crawley.data.paths import ensure_data_dirs

    ensure_data_dirs()
    init_schema()

    parser = build_parser()
    args = parser.parse_args(argv)
    _configure_logging(args.verbose)

    # Local executor unused for once/watch (worker runs on this thread) but
    # keeps import side-effects consistent if modules expect a pool later.
    with ThreadPoolExecutor(max_workers=2, thread_name_prefix="asx-scanner"):
        if args.command == "status":
            return cmd_status()
        if args.command == "once":
            return cmd_once(force=bool(args.force))
        if args.command == "watch":
            try:
                return cmd_watch(poll_s=float(args.poll), force_default=bool(args.force))
            except KeyboardInterrupt:
                print("\nStopped.", file=sys.stderr)
                return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
