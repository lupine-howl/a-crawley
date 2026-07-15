# Product

**Working title:** Crawley  
**Status:** Brief confirmed; **Sprints 1–10 closed**; **Sprint 11 ready** — Sender Inbox + ASX PoCs (former planned 11–40 [shelved](docs/sprints/shelved/README.md))

## Problem

A single person’s life spans many systems—email, calendar, fitness, co-parenting, DIY, work, coding/creative projects, personal finance, taxes, and investing. Today that means tab-hopping, ad-hoc searches, and mental juggling with little joined-up analysis.

**Who feels it:** The stakeholder alone (personal use). There is no commercial audience in scope.

**What exists instead:** Manual browsing, separate apps (Gmail, Calendar, etc.), and occasional LLM chats without durable local structure or pluggable life modules.

## Product vision

Crawley is a **local-first, AI-rich personal assistant** that runs on the stakeholder’s machine. It collects data from configured sources, analyzes it with ML/LLMs, and surfaces advice through a modular desktop-facing dashboard.

- **Brain:** Python, with a rich ML stack; OpenAI API for prototyping; path to a locally hosted LLM (e.g. Llama variant) after PoC.
- **Shape:** Shared core + **pluggable modules** behind a stable contract (read now; write-back later).
- **Surface:** Local **browser UI** on the machine (easy desktop use; optional phone-on-LAN testing later). Optional native desktop shell around the same UI is a later enhancement—not a parallel product.

## Target users

- **Primary:** The stakeholder (sole operator and beneficiary).
- **Secondary:** None for the foreseeable future (no multi-user, no family/co-parent accounts).

## Goals

Measurable outcomes, not a feature laundry list:

1. **Local personal OS shell** — Open a dashboard, navigate modules, and run analysis through a clear module contract without re-plumbing the core each time a domain is added.
2. **Signal from real sources** — At least investment/web search and Google mail/calendar (read) can be pulled and turned into short, actionable summaries/advice the user can act on manually.
3. **Room to grow domains** — Health/fitness, co-parenting schedule, DIY, work, finance/taxes, coding/creative projects, and similar areas can be added as modules without forking the app.
4. **Privacy by locality** — Stay on the user’s machine; no public product hosting. Security focus is intrusion resistance for a personal setup (especially if LAN/phone access is enabled later), not multi-tenant SaaS controls.

## Non-goals

Explicitly out of scope for now (unless the roadmap moves them):

- Public hosting, SaaS, or commercial packaging
- Multi-user / accounts / co-parent shared login
- Dedicated native mobile app (browser-on-phone testing may be enabled later; it is not a product requirement)
- Local LLM setup and ops **before** a working PoC on the cloud LLM path
- Automated trading / order placement (may return as a later/icebox idea)
- Medical diagnosis or regulated advice framed as professional care
- Live write-back before designed confirm-first path (ADR-006); silent/scheduled mutations without explicit confirm
- Building two separate UI stacks (e.g. Qt *and* web) for the same PoC

## Constraints

| Area | Constraint |
|------|------------|
| Runtime | Python for core, modules, scraping, analysis, LLM calls |
| UI (Now) | Local browser UI served from the machine |
| UI (Later) | Optional native desktop wrapper reusing the same UI |
| LLM | OpenAI API for prototyping; local Llama-class model after PoC proves value |
| Google | Single Google identity; **read-only** through Sprint 5; confirm-first write-back scheduled (Calendar → Gmail) per roadmap |
| Advice model | Summaries and suggestions the user applies manually; no automated financial or medical action |
| Audience | Personal use only |
| Security | Practical intrusion resistance for a local (and optionally LAN) app; not enterprise compliance theater |

## Success metrics

| Metric | Target | Notes |
|--------|--------|-------|
| PoC usefulness | Can open dashboard, hit investment + Gmail/Calendar flows, get LLM-synthesized output from real reads/searches | **Met** after Sprints 1–5; Fitness/Work lite also live |
| Module extensibility | New domain can be added behind the shared module contract without rewriting the core | Contract defined early |
| Habit / pull | Stakeholder chooses to open Crawley for at least one real decision or summary in a normal week once PoC works | Qualitative but explicit |
| Privacy posture | No public deployment; secrets stay local; remote surface minimized (localhost by default) | LAN/phone access only if consciously enabled later |
| Path to local LLM | PoC proven on OpenAI before investing in local model hosting | Milestone, not day-one |

## Modular domains (intent)

Pluggable areas envisioned over time (priority lives in `ROADMAP.md`):

- Investment / market & sentiment signals (web scrape/search + synthesis)
- Email (Gmail)
- Calendar
- Health & fitness
- Co-parenting schedule
- DIY projects
- Work tasks
- Personal finance, taxes
- Coding & creative projects
- Additional life domains as modules

## Decisions log (Interview 1)

- Working title: **Crawley**
- Python brain + local browser UI for Now; optional desktop shell Later
- Personal sole user; no commercial hosting
- Write-back deferred but architecturally anticipated
- Local LLM important after PoC, not before
- Automated trading deferred (Later / Icebox)

## Decisions log (Sprints 6–10 planning)

- Sequence after Sprint 5: life stubs (**Co-parenting + DIY** → **Finance + Day brief**) before first **Calendar write-back**, then **Local LLM**, then **Coding/Creative + shared context seed**
- Gmail send deferred until Calendar write-back soaks; Day brief uses snapshot composition (not overnight cron) in Sprint 7

## Decisions log (Sprints 1–5 close + 11–20 planning)

- **Verdict:** PoC goals met; continue delivery (see retrospective)
- Sprints **6–10 delivered** (bundled); next delivery number is **11**
- Former planned **11–20 / 21–40** packages later **shelved** for Sender Inbox + ASX pivot
- Icebox stays out (live brokerage orders, multi-user, SaaS, e-file) without PRODUCT revision

## Decisions log (Sprints 21–40 — Email/Investment depth)

- Former depth arc (old 21–40) **shelved**; pivot supersedes for near-term Email/Investment work
- **Automated trading / live brokerage orders remain Icebox**; paper portfolio allowed in Sprint 13

## Decisions log (Pivot — Sender Inbox + ASX PoCs)

- After **Sprints 6–10 delivered**, next number is **Sprint 11** (not a reset to 6)
- **Shelve** former planned Sprints 11–40 depth/platform queue (B32–B64); restore later selectively
- **Gmail Next (11):** background one-email-at-a-time LLM categorization; UI **grouped by sender** with LLM **sender profiles** + **todos**; PoC **~20 emails**
- **Investment Next (12–13):** **ASX-first**; large universe; background scan; per-company **profiles**; sources + prompts; structured **recommendations**; **paper portfolio** (not live orders)
- UX expert designs both dashboards at Sprint 11 gate (`docs/ux/sender-inbox-asx.md`)
