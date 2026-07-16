"""JSON routes: /v1/gmail/… for crawley-ui Sender Inbox."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Request

from crawley.api.presentation import (
    GmailConnectionResponse,
    ScanActionResponse,
    SenderDetailResponse,
    SenderListResponse,
    present_gmail_connection,
    present_gmail_ingest_job,
    present_sender_detail,
    present_sender_list,
)

router = APIRouter(tags=["gmail-api"])


@router.get("/v1/gmail/connection", response_model=GmailConnectionResponse)
def gmail_connection() -> GmailConnectionResponse:
    return present_gmail_connection()


@router.get("/v1/gmail/senders", response_model=SenderListResponse)
def gmail_senders(
    query: str = Query(""),
    category: str = Query(""),
    todo: str = Query(""),
) -> SenderListResponse:
    return present_sender_list(query=query, category=category, todo=todo)


@router.get("/v1/gmail/senders/{sender_id}", response_model=SenderDetailResponse)
def gmail_sender_detail(sender_id: str) -> SenderDetailResponse:
    detail = present_sender_detail(sender_id)
    if detail is None:
        raise HTTPException(status_code=404, detail=f"Unknown sender: {sender_id}")
    return detail


@router.post("/v1/gmail/ingest/start", response_model=ScanActionResponse)
async def gmail_ingest_start(
    request: Request,
    force: bool = Query(False, description="Reset PoC inbox data and re-run"),
) -> ScanActionResponse:
    from crawley.sender_inbox.worker import start_ingest

    force_flag = force
    try:
        payload = await request.json()
        if isinstance(payload, dict) and "force" in payload:
            force_flag = bool(payload.get("force"))
    except Exception:  # noqa: BLE001
        pass
    ok, msg = start_ingest(request.app.state.executor, force=force_flag)
    return ScanActionResponse(ok=ok, message=msg, job=present_gmail_ingest_job())


@router.post("/v1/gmail/ingest/stop", response_model=ScanActionResponse)
def gmail_ingest_stop() -> ScanActionResponse:
    from crawley.sender_inbox.worker import stop_ingest

    ok, msg = stop_ingest()
    return ScanActionResponse(ok=ok, message=msg, job=present_gmail_ingest_job())


@router.post("/v1/gmail/ingest/pause", response_model=ScanActionResponse)
def gmail_ingest_pause() -> ScanActionResponse:
    from crawley.sender_inbox.worker import request_pause

    request_pause()
    return ScanActionResponse(
        ok=True,
        message="Pause requested.",
        job=present_gmail_ingest_job(),
    )


@router.post("/v1/gmail/ingest/resume", response_model=ScanActionResponse)
def gmail_ingest_resume(request: Request) -> ScanActionResponse:
    from crawley.sender_inbox.worker import resume_ingest

    ok, msg = resume_ingest(request.app.state.executor)
    return ScanActionResponse(ok=ok, message=msg, job=present_gmail_ingest_job())


@router.post("/v1/gmail/ingest/reset", response_model=ScanActionResponse)
def gmail_ingest_reset() -> ScanActionResponse:
    from crawley.sender_inbox.store import reset_poc_data
    from crawley.sender_inbox.worker import request_pause

    request_pause()
    reset_poc_data()
    return ScanActionResponse(
        ok=True,
        message="PoC inbox data reset.",
        job=present_gmail_ingest_job(),
    )
