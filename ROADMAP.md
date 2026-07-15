# Roadmap

Ordered outcomes (not tasks). Product owner owns this file.  
**Working title:** Crawley  
**Retro:** [Sprints 1–5](docs/sprints/archive/sprints-1-5-retrospective.md)

## Now

**PoC complete (Sprints 1–5 closed 2026-07-15)** — local modular shell with real signal.

- [x] Shared Python core + **stable module contract** (write-back designed; dry-run until live sprints).
- [x] Local **browser** dashboard: themes, Settings, Markdown, home At a glance.
- [x] **Investment** (lite → hardened) + **Gmail** + **Calendar** read paths with LLM summaries.
- [x] **Fitness** + **Work** lite modules; remaining domains stubbed/planned.
- [x] Opt-in **phone-on-LAN**; write-back **ADR-006** + dry-run hooks.

*Still out of Now:* local LLM ops, live mutations, native desktop wrapper, automated trading, multi-user, public hosting.

## Next

**Finish top-tier lite coverage, then mutations + local intelligence**

### Sprint 6 (ready) — Co-parenting + DIY lite
[`docs/sprints/current.md`](docs/sprints/current.md) · B19–B21

### Sprint 7 (planned) — Finance lite + Day brief
[`docs/sprints/planned/sprint-7.md`](docs/sprints/planned/sprint-7.md) · B22–B24

### Sprint 8 (planned) — Confirm-first Calendar write-back
[`docs/sprints/planned/sprint-8.md`](docs/sprints/planned/sprint-8.md) · B25–B26

### Sprint 9 (planned) — Local LLM operable
[`docs/sprints/planned/sprint-9.md`](docs/sprints/planned/sprint-9.md) · B27

### Sprint 10 (planned) — Coding/Creative + shared context seed
[`docs/sprints/planned/sprint-10.md`](docs/sprints/planned/sprint-10.md) · B28–B30

## Later (scheduled — Sprints 11–20)

**Thicker mutations, desktop chrome, memory, and domain depth**

| Sprint | Theme | File |
|--------|-------|------|
| 11 | Gmail confirm-first write-back | [sprint-11.md](docs/sprints/planned/sprint-11.md) |
| 12 | Native desktop shell wrapper | [sprint-12.md](docs/sprints/planned/sprint-12.md) |
| 13 | Opt-in scheduled Day brief | [sprint-13.md](docs/sprints/planned/sprint-13.md) |
| 14 | Co-parenting → Calendar publish | [sprint-14.md](docs/sprints/planned/sprint-14.md) |
| 15 | Snapshot history + context depth | [sprint-15.md](docs/sprints/planned/sprint-15.md) |
| 16 | Fitness import lite | [sprint-16.md](docs/sprints/planned/sprint-16.md) |
| 17 | Finance CSV import lite | [sprint-17.md](docs/sprints/planned/sprint-17.md) |
| 18 | Investment watchlist | [sprint-18.md](docs/sprints/planned/sprint-18.md) |
| 19 | LAN gate + local backup/export | [sprint-19.md](docs/sprints/planned/sprint-19.md) |
| 20 | Weekly review + shell polish | [sprint-20.md](docs/sprints/planned/sprint-20.md) |

Index: [`docs/sprints/planned/README.md`](docs/sprints/planned/README.md)

## Later (scheduled — Sprints 21–40)

**Deep Email + Investment** — stakeholder priority after Sprint 20.  
Overview: [`docs/sprints/planned/email-investment-depth-21-40.md`](docs/sprints/planned/email-investment-depth-21-40.md)

| Sprint | Theme | Focus | File |
|--------|-------|-------|------|
| 21 | Gmail thread digests | Email | [sprint-21.md](docs/sprints/planned/sprint-21.md) |
| 22 | Investment research notebook + thesis | Investment | [sprint-22.md](docs/sprints/planned/sprint-22.md) |
| 23 | Gmail VIP / local priority rules | Email | [sprint-23.md](docs/sprints/planned/sprint-23.md) |
| 24 | Investment watchlist news clusters | Investment | [sprint-24.md](docs/sprints/planned/sprint-24.md) |
| 25 | Gmail labels (confirm-first) | Email | [sprint-25.md](docs/sprints/planned/sprint-25.md) |
| 26 | Investment holdings journal (manual) | Investment | [sprint-26.md](docs/sprints/planned/sprint-26.md) |
| 27 | Gmail saved searches | Email | [sprint-27.md](docs/sprints/planned/sprint-27.md) |
| 28 | Investment earnings & events skim | Investment | [sprint-28.md](docs/sprints/planned/sprint-28.md) |
| 29 | Gmail attachment skim | Email | [sprint-29.md](docs/sprints/planned/sprint-29.md) |
| 30 | Investment citations & source quality | Investment | [sprint-30.md](docs/sprints/planned/sprint-30.md) |
| 31 | Gmail follow-up tracker | Email | [sprint-31.md](docs/sprints/planned/sprint-31.md) |
| 32 | Investment scenario & risk check | Investment | [sprint-32.md](docs/sprints/planned/sprint-32.md) |
| 33 | Gmail newsletter digest | Email | [sprint-33.md](docs/sprints/planned/sprint-33.md) |
| 34 | Investment theme/sector baskets | Investment | [sprint-34.md](docs/sprints/planned/sprint-34.md) |
| 35 | Gmail archive/trash batch | Email | [sprint-35.md](docs/sprints/planned/sprint-35.md) |
| 36 | Investment local in-panel alerts | Investment | [sprint-36.md](docs/sprints/planned/sprint-36.md) |
| 37 | Gmail people context | Email | [sprint-37.md](docs/sprints/planned/sprint-37.md) |
| 38 | Investment comparative analysis | Investment | [sprint-38.md](docs/sprints/planned/sprint-38.md) |
| 39 | Email × Investment signal bridge | Bridge | [sprint-39.md](docs/sprints/planned/sprint-39.md) |
| 40 | Playbooks + Gmail/Investment polish | Both | [sprint-40.md](docs/sprints/planned/sprint-40.md) |

Index: [`docs/sprints/planned/README.md`](docs/sprints/planned/README.md)

### After Sprint 40 (unscheduled)

- Offline full-mailbox index / heavier RAG only if 21–40 proves need
- Broker **read-only** statement import — only with explicit PRODUCT pull (still no trading)
- Revisit Icebox only via brief revision

## Icebox

Valuable or tempting, explicitly not sequenced:

- Commercial productization or public hosting
- Multi-user / family accounts
- Dedicated mobile app store binary
- **Automated trading / order placement**
- Anything framed as professional medical or financial advice liability product
- Tax e-file / bank aggregation SaaS
