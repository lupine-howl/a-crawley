# Sprint 7 — Finance lite + Day brief (planned)

**Status:** planned (activates after Sprint 6 closes)  
**Duration:** one symbolic week  
**Backlog refs:** B22, B23, B24  
**Depends on:** Sprint 3 Calendar + Gmail harden (for Day brief inputs); Sprint 2 home glance  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**UX:** Optional pass for Day brief composition on home (keep “one composition”; do not turn home into a widget dump)

## Goal

Land the last high-intent money-domain stub (**Finance/Taxes** lite — planning only) and give a stronger morning reason to reopen Crawley: a **Day brief** composed from Calendar + Gmail signals on home.

## Demo

Operator can:

1. Open Finance/Taxes, capture local planning notes/context, run an LLM Markdown overview with a clear non-advice disclaimer
2. On home, see a Day brief built from Calendar + Gmail snapshot inputs (partial/empty states honest)
3. See Finance on At a glance when a successful run exists
4. Still cannot file taxes, connect a bank, or place trades from the UI

## Committed

### S7.1 — Finance / taxes lite (B22)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B22 |

**Acceptance criteria:**

- [ ] Finance/Taxes leaves Coming soon
- [ ] Local context capture (notes / categories / questions) under `data/`
- [ ] Run → Markdown planning summary + explicit “not professional tax/financial advice” disclaimer
- [ ] Job status + success snapshot for home
- [ ] No brokerage/bank OAuth; no payments or e-file

---

### S7.2 — Home day brief (Calendar + Gmail) (B23)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B23 |
| Depends on | B6, B10, B14 |

**Acceptance criteria:**

- [ ] Home includes a **Day brief** Markdown section composed from Calendar + Gmail snapshot inputs
- [ ] Refresh path uses existing successful snapshots; does not invent content when a module never succeeded
- [ ] Partial states supported (Calendar only / Gmail only / neither)
- [ ] One composition — truncate; no schedule+inbox+promo clutter in the first viewport
- [ ] Documented in `docs/architecture.md`

---

### S7.3 — Home glance: Finance slot (B24)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B24 |
| Depends on | S7.1 |

**Acceptance criteria:**

- [ ] Home shows last Finance snapshot when present
- [ ] Glance participants list updated in architecture.md

**Out of scope (sprint):**

- Portfolio charts, brokerage APIs, automated trading
- Real write-back mutations (Sprint 8)
- Overnight scheduled digests

## Parking lot

- Include Work / Co-parenting in Day brief via shared context (Sprint 10)
- Tax-season checklist templates
