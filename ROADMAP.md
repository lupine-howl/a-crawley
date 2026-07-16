# Roadmap

Ordered outcomes (not tasks). Product owner owns this file.  
**Working title:** Crawley  
**Code check (2026-07-16):** Sprints **1–30** shipped (HTMX PoC + dual-desk depth).  
**Hard pivot:** Phone Preview UI + Python analytics — [`docs/migration-phone-preview.md`](docs/migration-phone-preview.md) · [ADR-009](docs/adr/009-phone-preview-analytics.md).

## Now

**Shipped (legacy PoC — keep as analytics brain, not product UI):**

- [x] ASX desk, Sender Inbox, Google OAuth, LLM, jobs, paper/notebook/citations/themes  
- [x] Confirm-first Gmail send/labels; Calendar insert (Calendar **shelved** from product surface in this pivot)  
- [x] Lite life modules (to be quarantined from product during migration)

**Pivot in progress:**

- [x] JSON API + OpenAPI for ASX + jobs (Sprint 31)  
- [x] `crawley-ui` on published Phone Preview + ASX pack (Sprint 32)  
- [x] Explicit ASX daemon entrypoint (Sprint 33)  
- [x] Gmail ingest daemon + Sender Inbox pack (Sprint 34)  
- [ ] Delete Jinja product UI; quarantine Calendar + lite modules (Sprint 35)

*Still out of Now:* live brokerage orders, public hosting, multi-user, Calendar product pack

## Next

**Migration band — Sprints 31–35** (active: Sprint 35)

### Sprint 31 (closed) — Analytics JSON API (ASX + jobs)
Versioned `/v1` ASX + job control; presentation DTOs; OpenAPI; freeze HTMX features.  
[`docs/sprints/archive/sprint-31-analytics-api.md`](docs/sprints/archive/sprint-31-analytics-api.md) · B91–B93

### Sprint 32 (closed) — crawley-ui + ASX pack
npm `crawley-ui` from published Phone Preview; proxy to analytics; `asxDeskPack`.  
[`docs/sprints/archive/sprint-32-crawley-ui-asx-pack.md`](docs/sprints/archive/sprint-32-crawley-ui-asx-pack.md) · B94–B95

### Sprint 33 (closed) — ASX daemon entrypoint
Clear `asx-scanner` process/entrypoint; job status via API (`CRAWLEY_ASX_WORKER=daemon`).  
[`docs/sprints/archive/sprint-33-asx-daemon.md`](docs/sprints/archive/sprint-33-asx-daemon.md) · B96 · [`docs/daemons/asx-scanner.md`](docs/daemons/asx-scanner.md)

### Sprint 34 (closed) — Gmail ingest daemon + Sender Inbox pack
`gmail-ingest` daemon (ASX-style); `/v1/gmail/…` senders + reports; `senderInboxPack` Start/Stop UX.  
[`docs/sprints/archive/sprint-34-gmail-api-pack.md`](docs/sprints/archive/sprint-34-gmail-api-pack.md) · B97–B98 · [`docs/daemons/gmail-ingest.md`](docs/daemons/gmail-ingest.md)

### Sprint 35 (current) — Cutover (delete HTMX, quarantine modules)
Remove Jinja product UI; quarantine Calendar + lite modules; Settings/ops in `crawley-ui`.  
[`docs/sprints/current.md`](docs/sprints/current.md) · B99–B100

### After Sprint 35

- Re-introduce Calendar as light daemon + pack if needed  
- Un-shelve selected former depth/platform items ([shelved](docs/sprints/shelved/README.md))  
- Icebox stays closed without PRODUCT revision  

## Closed

| Sprints | Theme | Evidence |
|---------|-------|----------|
| 1–30 | HTMX PoC → dual-desk depth | [`docs/sprints/archive/`](docs/sprints/archive/) |

## Later (shelved)

- Calendar product pack  
- Lite life modules as first-class packs  
- Former depth backlog B54–B64 / bare `sprint-31.md`…`40.md` collision stubs (not migration 31–35)  
- Platform Later: desktop shell, scheduled brief, LAN gate, backup, etc.  

## Icebox

- Commercial productization or public hosting  
- Multi-user / family accounts  
- **Live automated trading / order placement**  
- Professional medical/financial advice liability framing  
- Tax e-file / bank aggregation SaaS  
