# Roadmap

Ordered outcomes (not tasks). Product owner owns this file.  
**Working title:** Crawley  
**Retro:** [Sprints 1–5](docs/sprints/archive/sprints-1-5-retrospective.md)  
**Pivot (2026-07-15):** Sender-grouped Inbox + ASX investment PoCs — prior sprints 6–40 [shelved](docs/sprints/shelved/README.md)

## Now

**PoC complete (Sprints 1–5 closed 2026-07-15)** — local modular shell with real signal.

- [x] Shared Python core + **stable module contract** (write-back designed; dry-run until live sprints).
- [x] Local **browser** dashboard: themes, Settings, Markdown, home At a glance.
- [x] **Investment** (lite → hardened) + **Gmail** + **Calendar** read paths with LLM summaries.
- [x] **Fitness** + **Work** lite modules; remaining domains stubbed/planned.
- [x] Opt-in **phone-on-LAN**; write-back **ADR-006** + dry-run hooks.

## Next

**Sender Inbox + ASX depth PoCs** — redefine Gmail and Investment around background enrichment and bespoke dashboards.

### Sprint 6 (ready) — Sender Inbox PoC (+ UX contract)
Background one-at-a-time email categorize; inbox **grouped by sender**; LLM sender profiles; actionable todos; **~20 email** cap. UX expert locks both Sender Inbox and ASX dashboard IA before/at start.  
[`docs/sprints/current.md`](docs/sprints/current.md) · B65–B70

### Sprint 7 (planned) — ASX company scanner + profiles PoC
Large ASX universe list; background scan (price / market data / news sentiment); per-company profiles using pro-investor-style metrics & sources; **~20 company** PoC slice.  
[`docs/sprints/planned/sprint-7-asx-profiles.md`](docs/sprints/planned/sprint-7-asx-profiles.md) · B71–B74

### Sprint 8 (planned) — ASX recommendations + paper portfolio
Structured actionable recommendations; separate **simulated portfolio** page tracking paper trades from recommendations; brokerage/simulation settings.  
[`docs/sprints/planned/sprint-8-asx-paper-portfolio.md`](docs/sprints/planned/sprint-8-asx-paper-portfolio.md) · B75–B77

### After Sprint 8 (unscheduled Next)

- Scale Sender Inbox beyond 20 (incremental background pull, retention)
- Scale ASX coverage beyond 20 (rate limits, universe tiers)
- Un-shelve selected items from [shelved 6–40](docs/sprints/shelved/README.md) where they still fit (e.g. confirm-first write-back, local LLM)

## Later (shelved — do not start)

Former Next/Later packages parked for post-PoC:

- [Shelved README](docs/sprints/shelved/README.md) — life-domain sprints + Email/Investment depth arc (old 6–40)
- Planned files still on disk under `docs/sprints/planned/sprint-*.md` marked **shelved**

## Icebox

- Commercial productization or public hosting
- Multi-user / family accounts
- Dedicated mobile app store binary
- **Live automated trading / order placement at a real brokerage** (paper portfolio in Sprint 8 is explicitly *not* this)
- Anything framed as professional medical or financial advice liability product
- Tax e-file / bank aggregation SaaS
