# Roadmap

Ordered outcomes (not tasks). Product owner owns this file.  
**Working title:** Crawley

## Now

**Local shell + proof that modules and real sources work** — *Sprint 1 closed 2026-07-15*

- [x] Shared Python core with a **stable module contract** (lifecycle, config/credentials hooks, inputs/outputs; read paths first; **write-back reserved** for later).
- [x] Local **browser** dashboard: navigate modules; click into panels.
- [x] **Investment module PoC:** quick web search/crawl → LLM synthesis of findings into short advice/summary (OpenAI for prototyping).
- [x] **Gmail PoC:** read-only connection → inbox summary the user can skim. *(Calendar remains stub — real read is Next.)*
- [x] **Fitness module:** visible stub (panel + contract compliance).
- [x] Placeholders / registration for a sensible base set of other life modules (Coming soon panels).

*Still out of Now:* local LLM hosting, write-back, desktop wrapper, automated trading, multi-user, public hosting.

**In flight (Sprint 2):** themes + LLM settings/test + Markdown summaries + home At a glance — see **Next**.

## Next

**Harden the personal OS and deepen the highest-value modules**

- **Design polish (Sprint 2):** themable palette / better styling per `docs/ux.md` (custom CSS tokens; no Node).
- **Operator settings (Sprint 2):** dashboard control to configure the active LLM and **test the connection**.
- **Readable summaries (Sprint 2):** Markdown rendering in Investment/Gmail panels (safe HTML; theme-aware).
- **Home At a glance (Sprint 2):** persisted last Investment/Gmail summaries + status chips on dashboard home (habit / reopen pull).
- Strengthen investment and mail/calendar modules (richer analysis, clearer advice UX, better error/auth handling).
- Real **Calendar** read-only summary (may share Google OAuth with Gmail).
- Flesh out fitness beyond stub if it’s still pulling attention.
- Optional **phone-on-LAN** access pattern for the same browser UI (consciously enabled; intrusion-minded defaults).
- Begin wiring additional domain modules that matter day-to-day (e.g. co-parenting schedule, work tasks, finance)—still read/analyze/advise first.
- Prepare for **write-back** (design already allowed by contract): draft-only or explicit-confirm paths for calendar/email when ready.

## Later

**Local intelligence and thicker life coverage**

- Run on a **locally hosted LLM** (Llama-class or similar); reduce reliance on cloud APIs for core advice.
- Optional **native desktop shell** wrapping the existing web UI (dock icon / window)—not a second UI stack.
- Broader module set: DIY, coding/creative projects, taxes/finance depth, co-parenting workflows as needed.
- Selective write-back and automation with strong user confirmation.
- Stronger local data organisation across modules (shared memory/context across domains).

## Icebox

Valuable or tempting, explicitly not sequenced:

- Commercial productization or public hosting
- Multi-user / family accounts
- Dedicated mobile app store binary
- **Automated trading / order placement**
- Anything framed as professional medical or financial advice liability product
