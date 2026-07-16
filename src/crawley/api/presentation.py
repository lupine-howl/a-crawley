"""Presentation DTOs for `/v1` — stable shapes for crawley-ui.

Worker store (DuckDB / `data/investment/asx/*.json`) is private scratch.
These builders publish only presentation fields. UI must not read raw
worker paths or scrape Yahoo/Gmail/LLM itself.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from crawley.asx_desk.store import company_detail, desk_rows, progress_view
from crawley.asx_desk.worker import is_running
from crawley import __version__

ASX_SCAN_JOB_ID = "asx-scan"
GMAIL_INGEST_JOB_ID = "gmail-ingest"

JobStatus = Literal["idle", "busy", "paused", "done", "error", "queued"]


class HealthResponse(BaseModel):
    ok: bool = True
    service: str = "crawley-analytics"
    version: str = __version__
    asx_worker: str = Field(
        default="in_process",
        description="in_process | daemon (CRAWLEY_ASX_WORKER)",
    )
    gmail_worker: str = Field(
        default="in_process",
        description="in_process | daemon (CRAWLEY_GMAIL_WORKER)",
    )


class CompanyListItem(BaseModel):
    ticker: str
    name: str
    sector: str
    scan_status: str = Field(description="pending | ready | error | …")
    change_pct: float | None = None
    move: str = "—"
    sentiment: str = "unknown"
    scanned_at: str = ""
    error: str = ""


class CompanyListResponse(BaseModel):
    companies: list[CompanyListItem]
    count: int
    active_set_size: int = Field(description="Tickers in the current PoC / active set")


class SnapshotDTO(BaseModel):
    price: float | None = None
    change_pct: float | None = None
    volume: float | None = None
    currency: str = "AUD"
    sentiment: str = "unknown"
    headline: str = ""
    as_of: str = ""
    gaps: list[str] = Field(default_factory=list)


class HeadlineDTO(BaseModel):
    title: str = ""
    url: str = ""
    source: str = ""


class ProfileDTO(BaseModel):
    status: str = "empty"
    markdown: str = ""
    error: str = ""
    updated_at: str = ""


class CompanyDetailResponse(BaseModel):
    ticker: str
    name: str
    sector: str
    scan_status: str = "pending"
    snapshot: SnapshotDTO
    move: str = "—"
    headlines: list[HeadlineDTO] = Field(default_factory=list)
    sources_used: list[str] = Field(default_factory=list)
    profile: ProfileDTO
    disclaimer: str = "Not licensed research — operator notes and desk synthesis only."


class JobProgressDTO(BaseModel):
    processed: int = 0
    total: int = 0
    remaining: int = 0
    current_ticker: str = ""
    current_item: str = Field(
        default="",
        description="Current subject/line for non-ASX jobs (e.g. gmail-ingest)",
    )


class JobStatusResponse(BaseModel):
    id: str
    kind: str
    status: JobStatus
    message: str = ""
    error: str = ""
    progress: JobProgressDTO
    updated_at: str = ""
    pause_requested: bool = False


class JobListResponse(BaseModel):
    jobs: list[JobStatusResponse]


class ScanActionResponse(BaseModel):
    ok: bool
    message: str
    job: JobStatusResponse


class SenderListItem(BaseModel):
    sender_id: str
    display_name: str
    from_name: str = ""
    from_addr: str = ""
    message_count: int = 0
    latest_at: str = ""
    signals: list[str] = Field(default_factory=list)
    open_todos: int = 0
    has_profile: bool = False
    categories: list[str] = Field(default_factory=list)
    rule_priority: str = ""


class SenderListResponse(BaseModel):
    senders: list[SenderListItem]
    count: int
    google_connected: bool = False


class SenderMessageDTO(BaseModel):
    id: str = ""
    subject: str = ""
    snippet: str = ""
    internal_date: str = ""
    signals: list[str] = Field(default_factory=list)
    category: str = ""
    error: str = ""


class SenderTodoDTO(BaseModel):
    id: str = ""
    text: str = ""
    done: bool = False
    created_at: str = ""


class SenderDetailResponse(BaseModel):
    sender_id: str
    display_name: str
    from_name: str = ""
    from_addr: str = ""
    message_count: int = 0
    profile: ProfileDTO
    messages: list[SenderMessageDTO] = Field(default_factory=list)
    todos: list[SenderTodoDTO] = Field(default_factory=list)
    open_todo_count: int = 0


class GmailConnectionResponse(BaseModel):
    connected: bool
    client_ok: bool = False
    error: str = ""
    oauth_start_path: str = Field(
        default="/modules/gmail/oauth/start",
        description="Relative path on analytics host for Connect Google",
    )


def present_company_list() -> CompanyListResponse:
    rows = desk_rows()
    companies = [
        CompanyListItem(
            ticker=r["ticker"],
            name=r.get("name") or r["ticker"],
            sector=r.get("sector") or "—",
            scan_status=str(r.get("status") or "pending"),
            change_pct=r.get("change_pct"),
            move=str(r.get("move") or "—"),
            sentiment=str(r.get("sentiment") or "unknown"),
            scanned_at=str(r.get("scanned_at") or ""),
            error=str(r.get("error") or ""),
        )
        for r in rows
    ]
    return CompanyListResponse(
        companies=companies,
        count=len(companies),
        active_set_size=len(companies),
    )


def present_company_detail(ticker: str) -> CompanyDetailResponse | None:
    detail = company_detail(ticker)
    if detail is None:
        return None
    scan = detail.get("scan") or {}
    snap = detail.get("snapshot") or {}
    profile = detail.get("profile") or {}
    headlines: list[HeadlineDTO] = []
    for h in detail.get("headlines") or []:
        if not isinstance(h, dict):
            continue
        headlines.append(
            HeadlineDTO(
                title=str(h.get("title") or ""),
                url=str(h.get("url") or ""),
                source=str(h.get("source") or ""),
            )
        )
    return CompanyDetailResponse(
        ticker=detail["ticker"],
        name=detail.get("name") or detail["ticker"],
        sector=detail.get("sector") or "—",
        scan_status=str(scan.get("status") or "pending"),
        snapshot=SnapshotDTO(
            price=snap.get("price"),
            change_pct=snap.get("change_pct"),
            volume=snap.get("volume"),
            currency=str(snap.get("currency") or "AUD"),
            sentiment=str(snap.get("sentiment") or "unknown"),
            headline=str(snap.get("headline") or ""),
            as_of=str(snap.get("as_of") or ""),
            gaps=list(snap.get("gaps") or []),
        ),
        move=str(detail.get("move") or "—"),
        headlines=headlines,
        sources_used=[str(s) for s in (detail.get("sources_used") or [])],
        profile=ProfileDTO(
            status=str(profile.get("status") or "empty"),
            markdown=str(profile.get("markdown") or ""),
            error=str(profile.get("error") or ""),
            updated_at=str(profile.get("updated_at") or ""),
        ),
    )


def _map_job_status(progress: dict[str, Any]) -> JobStatus:
    raw = str(progress.get("status") or "idle")
    processed = int(progress.get("processed") or 0)
    total = int(progress.get("cap") or 0)
    if raw == "busy":
        return "busy"
    if raw == "queued":
        return "queued"
    if raw == "paused":
        return "paused"
    if raw == "error":
        return "error"
    if raw == "done":
        return "done"
    if raw == "idle" and total > 0 and processed >= total:
        return "done"
    return "idle"


def present_asx_scan_job() -> JobStatusResponse:
    from crawley.asx_desk.worker import external_worker_mode

    # Daemon mode: trust disk status (API process is not the worker).
    running = None if external_worker_mode() else is_running()
    progress = progress_view(running=running)
    status = _map_job_status(progress)
    message = str(progress.get("current_line") or "")
    if not message:
        if status == "busy":
            message = "ASX scan in progress…"
        elif status == "queued":
            message = "Queued for asx-scanner daemon…"
        elif status == "paused":
            message = "ASX scan paused."
        elif status == "done":
            message = "Active set scanned."
        else:
            message = "ASX scan idle."
    return JobStatusResponse(
        id=ASX_SCAN_JOB_ID,
        kind="asx_scan",
        status=status,
        message=message,
        error=str(progress.get("last_error") or ""),
        progress=JobProgressDTO(
            processed=int(progress.get("processed") or 0),
            total=int(progress.get("cap") or 0),
            remaining=int(progress.get("remaining") or 0),
            current_ticker=str(progress.get("current_ticker") or ""),
        ),
        updated_at=str(progress.get("updated_at") or ""),
        pause_requested=bool(progress.get("pause_requested")),
    )


def _map_gmail_job_status(progress: dict[str, Any]) -> JobStatus:
    raw = str(progress.get("status") or "idle")
    if raw in {"busy", "queued", "paused", "error", "done"}:
        return raw  # type: ignore[return-value]
    return "idle"


def present_gmail_ingest_job() -> JobStatusResponse:
    from crawley.sender_inbox.store import progress_view as gmail_progress
    from crawley.sender_inbox.worker import external_worker_mode as gmail_external
    from crawley.sender_inbox.worker import is_running as gmail_running

    running = None if gmail_external() else gmail_running()
    progress = gmail_progress(running=running)
    status = _map_gmail_job_status(progress)
    message = str(progress.get("current_line") or "")
    if not message:
        if status == "busy":
            message = "Gmail ingest in progress…"
        elif status == "queued":
            message = "Queued for gmail-ingest daemon…"
        elif status == "paused":
            message = "Gmail ingest paused."
        elif status == "done":
            message = "Ingest complete (cap or no more candidates)."
        else:
            message = "Gmail ingest idle."
    current = str(progress.get("current_line") or "")
    return JobStatusResponse(
        id=GMAIL_INGEST_JOB_ID,
        kind="gmail_ingest",
        status=status,
        message=message,
        error=str(progress.get("last_error") or ""),
        progress=JobProgressDTO(
            processed=int(progress.get("processed") or 0),
            total=int(progress.get("cap") or 0),
            remaining=int(progress.get("remaining") or 0),
            current_ticker="",
            current_item=current[:120],
        ),
        updated_at=str(progress.get("updated_at") or ""),
        pause_requested=bool(progress.get("pause_requested")),
    )


def present_sender_list(
    *,
    query: str = "",
    category: str = "",
    todo: str = "",
) -> SenderListResponse:
    from crawley.google_oauth import google_auth_status
    from crawley.sender_inbox.store import group_senders

    rows = group_senders(query=query, category=category, todo=todo)
    senders = [
        SenderListItem(
            sender_id=str(r.get("sender_id") or ""),
            display_name=str(r.get("display_name") or "Unknown sender"),
            from_name=str(r.get("from_name") or ""),
            from_addr=str(r.get("from_addr") or ""),
            message_count=int(r.get("message_count") or 0),
            latest_at=str(r.get("latest_at") or ""),
            signals=[str(s) for s in (r.get("signals") or [])],
            open_todos=int(r.get("open_todos") or 0),
            has_profile=bool(r.get("has_profile")),
            categories=[str(c) for c in (r.get("categories") or [])],
            rule_priority=str(r.get("rule_priority") or ""),
        )
        for r in rows
    ]
    auth = google_auth_status()
    return SenderListResponse(
        senders=senders,
        count=len(senders),
        google_connected=bool(auth.get("connected")),
    )


def present_sender_detail(sender_id: str) -> SenderDetailResponse | None:
    from crawley.sender_inbox.schema import normalize_metrics
    from crawley.sender_inbox.store import sender_detail

    detail = sender_detail(sender_id)
    if detail is None:
        return None
    profile = detail.get("profile") or {}
    messages: list[SenderMessageDTO] = []
    for m in detail.get("messages") or []:
        if not isinstance(m, dict):
            continue
        metrics = normalize_metrics(m.get("metrics"))
        messages.append(
            SenderMessageDTO(
                id=str(m.get("id") or ""),
                subject=str(m.get("subject") or ""),
                snippet=str(m.get("snippet") or ""),
                internal_date=str(m.get("internal_date") or ""),
                signals=[str(s) for s in (m.get("signals") or [])],
                category=str(metrics.get("category") or ""),
                error=str(m.get("error") or ""),
            )
        )
    todos = [
        SenderTodoDTO(
            id=str(t.get("id") or ""),
            text=str(t.get("text") or t.get("title") or ""),
            done=bool(t.get("done")),
            created_at=str(t.get("created_at") or ""),
        )
        for t in (detail.get("todos") or [])
        if isinstance(t, dict)
    ]
    return SenderDetailResponse(
        sender_id=str(detail.get("sender_id") or sender_id),
        display_name=str(detail.get("display_name") or "Unknown sender"),
        from_name=str(detail.get("from_name") or ""),
        from_addr=str(detail.get("from_addr") or ""),
        message_count=int(detail.get("message_count") or 0),
        profile=ProfileDTO(
            status=str(profile.get("status") or "empty"),
            markdown=str(profile.get("markdown") or ""),
            error=str(profile.get("error") or ""),
            updated_at=str(profile.get("updated_at") or ""),
        ),
        messages=messages,
        todos=todos,
        open_todo_count=int(detail.get("open_todo_count") or 0),
    )


def present_gmail_connection() -> GmailConnectionResponse:
    from crawley.google_oauth import google_auth_status

    auth = google_auth_status()
    return GmailConnectionResponse(
        connected=bool(auth.get("connected")),
        client_ok=bool(auth.get("client_ok")),
        error=str(auth.get("error") or ""),
        oauth_start_path="/modules/gmail/oauth/start",
    )


def present_job(job_id: str) -> JobStatusResponse | None:
    if job_id == ASX_SCAN_JOB_ID:
        return present_asx_scan_job()
    if job_id == GMAIL_INGEST_JOB_ID:
        return present_gmail_ingest_job()
    return None


def present_jobs() -> JobListResponse:
    return JobListResponse(jobs=[present_asx_scan_job(), present_gmail_ingest_job()])
