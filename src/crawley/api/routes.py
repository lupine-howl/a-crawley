"""JSON routes: /health and /v1/… for crawley-ui."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, Query

from crawley.api.presentation import (
    ASX_SCAN_JOB_ID,
    CompanyDetailResponse,
    CompanyListResponse,
    HealthResponse,
    JobListResponse,
    JobStatusResponse,
    ScanActionResponse,
    present_asx_scan_job,
    present_company_detail,
    present_company_list,
    present_job,
    present_jobs,
)

router = APIRouter(tags=["analytics-api"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse()


@router.get("/v1/asx/companies", response_model=CompanyListResponse)
def asx_companies() -> CompanyListResponse:
    return present_company_list()


@router.get("/v1/asx/companies/{ticker}", response_model=CompanyDetailResponse)
def asx_company_detail(ticker: str) -> CompanyDetailResponse:
    detail = present_company_detail(ticker)
    if detail is None:
        raise HTTPException(status_code=404, detail=f"Unknown ticker: {ticker.upper()}")
    return detail


@router.post("/v1/asx/scan/start", response_model=ScanActionResponse)
async def asx_scan_start(
    request: Request,
    force: bool = Query(False, description="Re-run even if active set already scanned"),
) -> ScanActionResponse:
    from crawley.asx_desk.worker import start_scan

    # Prefer JSON body `{ "force": true }` when present; else query `?force=true`.
    force_flag = force
    try:
        payload = await request.json()
        if isinstance(payload, dict) and "force" in payload:
            force_flag = bool(payload.get("force"))
    except Exception:  # noqa: BLE001
        pass
    ok, msg = start_scan(request.app.state.executor, force=force_flag)
    return ScanActionResponse(ok=ok, message=msg, job=present_asx_scan_job())


@router.post("/v1/asx/scan/stop", response_model=ScanActionResponse)
def asx_scan_stop() -> ScanActionResponse:
    from crawley.asx_desk.worker import stop_scan

    ok, msg = stop_scan()
    return ScanActionResponse(ok=ok, message=msg, job=present_asx_scan_job())


@router.post("/v1/asx/scan/pause", response_model=ScanActionResponse)
def asx_scan_pause() -> ScanActionResponse:
    from crawley.asx_desk.worker import request_pause

    request_pause()
    return ScanActionResponse(
        ok=True,
        message="Pause requested.",
        job=present_asx_scan_job(),
    )


@router.post("/v1/asx/scan/resume", response_model=ScanActionResponse)
def asx_scan_resume(request: Request) -> ScanActionResponse:
    from crawley.asx_desk.worker import resume_scan

    ok, msg = resume_scan(request.app.state.executor)
    return ScanActionResponse(ok=ok, message=msg, job=present_asx_scan_job())


@router.post("/v1/asx/scan/reset", response_model=ScanActionResponse)
def asx_scan_reset() -> ScanActionResponse:
    from crawley.asx_desk.store import reset_poc_data
    from crawley.asx_desk.worker import request_pause

    request_pause()
    reset_poc_data()
    return ScanActionResponse(
        ok=True,
        message="PoC scan data reset.",
        job=present_asx_scan_job(),
    )


@router.get("/v1/jobs", response_model=JobListResponse)
def jobs_list() -> JobListResponse:
    return present_jobs()


@router.get("/v1/jobs/{job_id}", response_model=JobStatusResponse)
def jobs_get(job_id: str) -> JobStatusResponse:
    job = present_job(job_id)
    if job is None:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown job id: {job_id}. Known: {ASX_SCAN_JOB_ID}",
        )
    return job
