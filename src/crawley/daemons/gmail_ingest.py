"""Gmail / Sender Inbox ingest daemon — owns the ingest loop outside the API.

Usage:

    # One-shot (run until complete / paused / cap)
    uv run python -m crawley.daemons.gmail_ingest once --force

    # Watch for API-queued starts (set CRAWLEY_GMAIL_WORKER=daemon on the API)
    uv run python -m crawley.daemons.gmail_ingest watch

    # Print disk job status
    uv run python -m crawley.daemons.gmail_ingest status

Also installed as console script: ``crawley-gmail-ingest``.
"""

from __future__ import annotations

import argparse
import json
import logging
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
        format="%(asctime)s %(levelname)s [gmail-ingest] %(message)s",
        datefmt="%H:%M:%S",
    )


def cmd_status() -> int:
    from crawley.api.presentation import present_gmail_ingest_job
    from crawley.sender_inbox.worker import external_worker_mode

    job = present_gmail_ingest_job()
    payload = job.model_dump()
    payload["worker_mode"] = "daemon" if external_worker_mode() else "in_process"
    print(json.dumps(payload, indent=2))
    return 0


def cmd_once(*, force: bool) -> int:
    from crawley.sender_inbox.worker import run_ingest_in_this_process

    ok, msg = run_ingest_in_this_process(force=force)
    print(msg)
    return 0 if ok else 1


def cmd_watch(*, poll_s: float, force_default: bool) -> int:
    """Poll ingest_state for API-queued starts and run them in this process."""
    from crawley.sender_inbox.worker import claim_queued_ingest, run_ingest_in_this_process

    logging.info(
        "Watching for queued ingest (poll=%.1fs). "
        "API should set CRAWLEY_GMAIL_WORKER=daemon.",
        poll_s,
    )
    while True:
        if claim_queued_ingest():
            logging.info("Claiming queued ingest…")
            ok, msg = run_ingest_in_this_process(force=force_default)
            logging.info("%s", msg)
            if not ok:
                time.sleep(poll_s)
                continue
        time.sleep(poll_s)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crawley-gmail-ingest",
        description="Crawley Sender Inbox ingest daemon (threads OK; no Celery).",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    sub = parser.add_subparsers(dest="command", required=True)

    once = sub.add_parser("once", help="Run one ingest to completion in this process")
    once.add_argument(
        "--force",
        action="store_true",
        help="Reset PoC inbox data and re-run from an empty set",
    )

    watch = sub.add_parser(
        "watch",
        help="Loop: claim start_requested from API (CRAWLEY_GMAIL_WORKER=daemon)",
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
    from crawley.data.duck import init_schema
    from crawley.data.paths import ensure_data_dirs

    ensure_data_dirs()
    init_schema()

    parser = build_parser()
    args = parser.parse_args(argv)
    _configure_logging(args.verbose)

    with ThreadPoolExecutor(max_workers=2, thread_name_prefix="gmail-ingest"):
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
