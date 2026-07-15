# Sprint 13 — Scheduled Day brief / local jobs (planned)

**Status:** planned (activates after Sprint 7 Day brief + Sprint 10 context preferred)  
**Duration:** one symbolic week  
**Backlog refs:** B33  
**Depends on:** B23 (Day brief), B12 (LAN awareness — jobs must not widen exposure)  
**Architecture:** In-process scheduler vs system cron — architect chooses; document  
  
## Goal

Give Crawley a **conscious local schedule** for refreshing Day brief (and optionally one module skim) without becoming a cloud push product. Default off; operator enables.

## Demo

1. Enable a local schedule (e.g. weekday morning) in Settings
2. On trigger, Day brief refreshes from bounded sources/snapshots
3. Disable returns to fully manual runs
4. No remote notifications; no write-back from schedule

## Committed

### S13.1 — Opt-in local scheduler for Day brief (B33)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B33 |

**Acceptance criteria:**

- [ ] Settings: enable/disable + simple cadence; default **off**
- [ ] Scheduled job updates Day brief (and documents which fetches it may run)
- [ ] **No scheduled write-back** (ADR-006 holds)
- [ ] Missed-run / app-asleep behavior documented honestly
- [ ] Job status visible; errors do not clobber last good brief without policy note

**Out of scope:** Push email/SMS digests, always-on daemon productization beyond single process
