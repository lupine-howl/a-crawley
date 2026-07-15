# Sprint 11 — Update-from-git + Sender Inbox PoC

**Status:** ready (next delivery after Sprints 6–10 closed)  
**Duration:** one symbolic week  
**Backlog refs:** B78, B65, B66, B67, B68, B69, B70  
**Depends on:** Sprints 1–10 shell; UX draft for Sender Inbox / ASX (`docs/ux/sender-inbox-asx.md`)  
**Architecture:** [`docs/architecture.md`](../architecture.md) — document Update + reload behaviour  
**UX:** Settings → **Update** control; Sender Inbox per [`docs/ux/sender-inbox-asx.md`](../ux/sender-inbox-asx.md)  
**Previous:** [`archive/sprint-6-10-life-modules-llm-context.md`](archive/sprint-6-10-life-modules-llm-context.md)  
**Planned source:** [`planned/sprint-11-sender-inbox.md`](planned/sprint-11-sender-inbox.md)

## Goal

1. **First:** Let the operator pull latest app code from git via **Settings → Update** (or equivalent dashboard control) and **prove hot reload** picks up the change when `CRAWLEY_RELOAD` is enabled.  
2. **Then:** Ship the **Sender Inbox PoC** (~20 emails): one-at-a-time categorize → grouped-by-sender → LLM profiles → todos.  
3. ASX Investment PoC follows in **Sprints 12–13** (already planned).

## Demo

Operator can:

1. Open Settings → **Update**, run **Pull latest**, see clear success/failure (commit before/after or short log)
2. With hot reload on (`CRAWLEY_RELOAD=1`), confirm the running app **reloads** after a pull that changes watched files (documented proof — e.g. UI notice + process reload, or test)
3. Use Sender Inbox PoC: ingest ~20 mails one-by-one → sender groups → profile + todos
4. Restart still shows categorized data / profiles / todos under `data/`

## Committed

Implement **in order** (S11.0 → S11.1 → Sender Inbox stories). Architect may start S11.0 immediately; treat UX draft as accepted for Sender Inbox unless stakeholder revises `docs/ux/sender-inbox-asx.md`.

### S11.0 — Settings Update: git pull + hot reload (B78)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B78 |
| Priority | first in sprint |

**Acceptance criteria:**

- [ ] **Settings → Update** (preferred) or equally discoverable dashboard control with section title **Update**
- [ ] **Pull latest** action runs `git pull` (or equivalent fetch+merge/ff) in the app repo from the local process; shows result in UI (ok / already up to date / error with short reason)
- [ ] Documented **precondition**: `CRAWLEY_RELOAD=1` (or Settings toggle that enables reload) so file changes under `src/crawley/` trigger Uvicorn reload after pull
- [ ] **Proof of hot reload:** after a successful pull that touches watched paths, operator sees reload behaviour (e.g. brief “Reloading…” / new request served by restarted worker); covered by automated test *or* documented manual demo steps in README
- [ ] Safe defaults: action available on **localhost** (disable or hard-warn on LAN bind); never logs secrets; fails cleanly if not a git checkout / no network / merge conflict
- [ ] Brief note in `docs/architecture.md` + README Update section
- [ ] No auto-pull on a schedule this sprint

**Out of scope:**

- GitHub Apps / cloud deploy / CI from this button
- Resolving merge conflicts in UI
- Pulling while multiple remotes/branches without documenting the branch used (track current branch / `main` — document choice)

---

### S11.1 — UX contract confirm (Sender Inbox + ASX) (B65)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B65 |
| Depends on | — (draft already exists) |

**Acceptance criteria:**

- [ ] Stakeholder accepts `docs/ux/sender-inbox-asx.md` as implement contract (or lands small amendments)
- [ ] Includes Settings → Update placement note (under Settings chrome; quiet, not a hero widget)
- [ ] ASX surfaces remain specified for Sprints 12–13

---

### S11.2 — Background email ingest + LLM categorize (B66)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B66 |
| Depends on | S11.1 |

**Acceptance criteria:**

- [ ] Background worker pulls **one email at a time**
- [ ] Each message LLM-categorized onto a documented metric set (schema in architecture)
- [ ] Progress visible; failures isolate one message
- [ ] Existing Google read path; no write-back required

---

### S11.3 — Sender-grouped Inbox view (B67)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B67 |
| Depends on | S11.2 |

**Acceptance criteria:**

- [ ] Primary Inbox surface **grouped by sender**
- [ ] Drill-in to sender’s ingested messages; metric chips per UX
- [ ] Theme tokens only

---

### S11.4 — LLM sender profiles (B68)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B68 |
| Depends on | S11.3 |

**Acceptance criteria:**

- [ ] LLM profile per sender with ingested mail; regenerate on new mail or refresh
- [ ] Persisted under `data/`; shown on sender detail

---

### S11.5 — Actionable todos from sender bundles (B69)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B69 |
| Depends on | S11.4 |

**Acceptance criteria:**

- [ ] Todos extracted from sender bundle; open/done local toggle
- [ ] No auto-send / auto-calendar

---

### S11.6 — PoC cap ~20 emails (B70)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B70 |
| Depends on | S11.2 |

**Acceptance criteria:**

- [ ] Hard stop ~20; remaining capacity visible; reset path documented

## Explicitly out of sprint

- **ASX Investment PoC** → **Sprint 12** (profiles/scanner) then **Sprint 13** (recommendations + paper portfolio)
- Full mailbox crawl; Gmail send; live brokerage orders
- Shelved former planned 11–40 depth queue

## Parking lot

- “Update & restart” without relying on `CRAWLEY_RELOAD`
- Show current git SHA in Settings footer always
- Un-shelve Gmail confirm-first send after Sender Inbox PoC
