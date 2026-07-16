# Migration — Phone Preview UI + analytics daemons

**Status:** Migration band **31–35 complete** (2026-07-16)  
**ADR:** [`adr/009-phone-preview-analytics.md`](adr/009-phone-preview-analytics.md)  
**Archive:** [`sprints/archive/sprint-35-cutover.md`](sprints/archive/sprint-35-cutover.md)  

**UI consume recipe:** [`build/consuming-published-core.md`](build/consuming-published-core.md)

## Target shape

```
┌─────────────────────────────────────────────┐
│  crawley-ui (npm / Phone Preview host)        │
│  packs: ASX desk · Sender Inbox · Settings    │
│  UI persistence: IndexedDB (± Turso/Duck sync)│
└──────────────────────┬──────────────────────┘
                       │ HTTP JSON  /v1/…
┌──────────────────────▼──────────────────────┐
│  Crawley analytics (this repo — FastAPI)      │
│  · presentation read APIs · job control       │
│  · Google OAuth callbacks · health            │
└──────────┬─────────────────────┬────────────┘
           │                     │
┌──────────▼──────────┐  ┌───────▼────────────────┐
│  Daemon workers     │  │  Worker / presentation   │
│  asx-scanner        │→ │  DuckDB + data/ files    │
│  gmail-ingest       │  │  (API serves DTOs/views) │
└─────────────────────┘  └──────────────────────────┘
```

**Rule:** UI never talks to Yahoo / Gmail / LLM directly.

## Kept vs dropped

| Keep (analytics + UI packs) | Drop from product surface (quarantine / remove) |
|-----------------------------|--------------------------------------------------|
| ASX desk (Investment) | Fitness, Co-parenting, DIY, Work, Finance, Coding |
| Sender Inbox (Gmail) | Calendar (bring back later as light daemon + pack) |
| Google OAuth, LLM, jobs | Jinja/HTMX product shell (delete after API coverage) |
| Paper / notebook / citations / themes (via API later) | Former depth backlog 31–40 until post-migration |

## UI setup (`crawley-ui`)

- Install / scaffold via **npm** using **published** `@phone-preview/*` packages; run as **`crawley-ui`**.
- Phone Preview ships a **light backend** for persistence sync (Turso); local-first path is primarily **IndexedDB**. Duck may be a UI persistence option — confirm against current Phone Preview docs/code.
- Dev: Vite proxy `/api/analytics` → analytics host (e.g. `http://127.0.0.1:8000`).
- Do **not** use Phone Preview’s tiny `--with-api` sidecar as the analytics brain.

### Ask phone-preview team (recommended)

Yes — request a short **setup recipe** for a custom host (not education packs):

1. Exact `npm create` / package names and versions for a blank host + packs  
2. How Connections / IndexedDB / Turso sync are configured for a personal local app  
3. Recommended pattern for proxying an external analytics API  
4. How Settings should deep-link “Connect Google” to the analytics OAuth URL  

Pin their answer in the `crawley-ui` README once received.

## Analytics setup (this repo)

- Keep Python package `crawley`; docs name: **Crawley analytics**.
- Add versioned JSON API + OpenAPI under `/v1/…` (ASX + jobs first).
- OAuth redirect URIs stay on the analytics host.
- Freeze Jinja feature work; **delete** product HTML when ASX + Gmail packs cover the operator loop. No permanent `/ops` HTML UI — ops live in `crawley-ui`.

## Phases → sprints

| Phase | Sprint | Outcome |
|-------|--------|---------|
| API + schema | **31** (closed) | OpenAPI; ASX companies/jobs JSON; presentation DTOs; freeze HTMX features |
| UI host + pack | **32** (closed) | `crawley-ui` scaffold; `asxDeskPack` list + start scan |
| Daemonize ASX | **33** (closed) | Clear `asx-scanner` entrypoint; status via API |
| Gmail path | **34** (closed) | `gmail-ingest` daemon + `/v1/gmail/…` + `senderInboxPack` (Start/Stop) |
| Cutover | **35** (closed) | Jinja product UI deleted; Calendar + lite quarantined; Settings/ops in UI |

## What not to do

- Rebuild ASX/Gmail in TypeScript  
- Put OpenAI/Google secrets in Vite  
- Iframe HTMX  
- Force education-curriculum packs  
- Block on Turso before `/v1` is stable  
- Un-shelve old depth 31–40 or Calendar until cutover works  

## Ownership

| Repo | Owns |
|------|------|
| `a-crawley` | JSON API, daemons, worker DB, OAuth, LLM, OpenAPI |
| `crawley-ui` | Shell, packs, Connections, job controls, UI persistence |
| Shared contract | OpenAPI + presentation field docs — versioned in `a-crawley` |
