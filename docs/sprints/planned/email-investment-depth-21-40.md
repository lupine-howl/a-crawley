# Arc — Email & Investment depth (Sprints 21–40)

**Stakeholder direction:** After Sprint 20, prioritize **deep functionality** for **Gmail** and **Investment**.  
**Non-negotiables:** local-first; confirm-first mutations (ADR-006); **no automated trading / order placement**; advice remains manually applied; single Google identity.

## Rhythm

Alternating focus keeps both modules advancing without starving either:

| Band | Sprints | Emphasis |
|------|---------|----------|
| Read depth | 21–24 | Thread digests, thesis notebook, VIP rules, news clusters |
| Hygiene & ledger | 25–28 | Labels, holdings journal, saved searches, earnings skim |
| Evidence & tracking | 29–32 | Attachments, citations, follow-ups, scenario/risk |
| Scale & operate | 33–36 | Newsletters, baskets, archive/trash batch, local alerts |
| Synthesis | 37–40 | People context, A vs B compare, mail×holdings bridge, playbooks/polish |

## Depends on (from 6–20)

Prefer these landed before or early in the arc:

- Gmail harden + write-back send (3–4, 11)
- Investment harden + watchlist (4, 18)
- Snapshot history / shared context (15) — improves digests & notebooks
- Scheduler (13) — optional for alerts (36)

## Icebox (still out)

- Brokerage order APIs / automated trading
- Multi-user / family inboxes
- Public hosting
- Full “Bloomberg terminal” market data contracts

## Success for the arc

Operator uses Crawley weekly to (1) triage mail with thread digests + follow-ups, and (2) run watchlist/basket research with notebook + citations — without needing a broker integration or leaving localhost.
