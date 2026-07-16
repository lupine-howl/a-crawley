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

JobStatus = Literal["idle", "busy", "paused", "done", "error"]


class HealthResponse(BaseModel):
    ok: bool = True
    service: str = "crawley-analytics"
    version: str = __version__


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
    progress = progress_view(running=is_running())
    status = _map_job_status(progress)
    message = str(progress.get("current_line") or "")
    if not message:
        if status == "busy":
            message = "ASX scan in progress…"
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


def present_job(job_id: str) -> JobStatusResponse | None:
    if job_id == ASX_SCAN_JOB_ID:
        return present_asx_scan_job()
    return None


def present_jobs() -> JobListResponse:
    return JobListResponse(jobs=[present_asx_scan_job()])
