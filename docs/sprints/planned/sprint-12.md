# Sprint 12 — Native desktop shell wrapper (planned)

**Status:** shelved (deferred — Sender Inbox + ASX PoC pivot)  
**Duration:** one symbolic week  
**Backlog refs:** B32  
**Depends on:** Stable local browser UI (Sprint 2+); localhost bind  
**Architecture:** ADR for wrapper choice (e.g. pywebview / Tauri / Electron — architect picks; **reuse existing UI**, no second stack)  
**UX:** Optional pass for window chrome only; product UI stays the web shell

## Goal

Optional **native desktop shell** around the existing web UI (dock icon / window), per Later roadmap — not a parallel Qt/product rewrite.

## Demo

1. Launch Crawley as a desktop window pointing at the local app
2. Same dashboard/modules work as in the browser
3. Documented start path beside `uv run python -m crawley`
4. Browser-only path remains fully supported

## Committed

### S12.1 — Desktop wrapper (B32)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B32 |

**Acceptance criteria:**

- [ ] Wrapper loads existing UI (localhost or embedded server start documented)
- [ ] README: install/run on stakeholder OS/WSL constraints
- [ ] Architecture ADR: technology choice + “one UI stack” confirmation
- [ ] Failure if server down surfaces clearly
- [ ] No duplicate feature implementation in native widgets

**Out of scope:** App-store packaging, auto-update SaaS, mobile app
