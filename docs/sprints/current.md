# Sprint 11 — Settings Update (git pull + hot reload)

**Status:** done  
**Duration:** one symbolic week  
**Backlog refs:** B78  
**Depends on:** Sprint 1 local run; `CRAWLEY_RELOAD` support in `__main__.py`  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**UX:** Quiet **Settings → Update** section (not a hero widget)  
**Previous:** [`archive/sprint-6-10-life-modules-llm-context.md`](archive/sprint-6-10-life-modules-llm-context.md)  
**Planned source:** [`planned/sprint-11-update.md`](planned/sprint-11-update.md)

## Goal

Let the operator **pull the latest app code from git** via **Settings → Update** and **prove hot reload** picks up changes when `CRAWLEY_RELOAD=1`.

Sender Inbox PoC is **Sprint 12** (not this sprint). ASX PoCs are Sprints **13–14**.

## Demo

1. Open Settings → **Update**
2. Run **Pull latest**; see success / already up to date / clear error
3. With `CRAWLEY_RELOAD=1`, a pull that changes watched files under `src/crawley/` triggers Uvicorn reload (documented proof and/or automated coverage)

## Committed

### S11.1 — Settings Update: git pull + hot reload (B78)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B78 |

**Acceptance criteria:**

- [x] **Settings → Update** section with **Pull latest**
- [x] Runs `git pull` (or fetch + ff-only) on the app checkout; UI shows ok / up-to-date / error with short reason
- [x] Documents **precondition** `CRAWLEY_RELOAD=1` so changes under `src/crawley/` trigger reload after pull
- [x] **Proof of hot reload:** documented README demo steps and/or automated test of pull plumbing + reload flag behaviour
- [x] Safe defaults: available on **localhost** and trusted **LAN/Tailscale** (warn when LAN-bound); never logs secrets; fails cleanly if not a git checkout / no network / non-ff / dirty blockers documented
- [x] Note in `docs/architecture.md` + README Update section
- [x] No scheduled auto-pull

**Out of scope (sprint):**

- Sender Inbox / ASX implementation
- GitHub Apps, CI deploy, conflict-resolution UI
- Multi-remote branch picker beyond documenting current branch

## Explicitly out of sprint

- **Sender Inbox PoC** → [`planned/sprint-12-sender-inbox.md`](planned/sprint-12-sender-inbox.md)
- **ASX PoCs** → Sprints 13–14
- Shelved former planned `sprint-11.md`…`sprint-40.md` depth queue

## Parking lot

- “Update & restart” without relying on `CRAWLEY_RELOAD`
- Always show current git SHA in Settings footer
