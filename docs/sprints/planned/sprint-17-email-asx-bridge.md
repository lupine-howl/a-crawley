# Sprint 17 — Email × ASX signal bridge (planned)

**Status:** planned (after Sprints 15–16 preferred)  
**Duration:** one symbolic week  
**Backlog refs:** B83  
**Depends on:** Sender Inbox store; ASX universe/profiles; paper portfolio helpful  
**UX:** One bridge composition with deep links (not a third dashboard)

## Goal

Cross-desk depth: scan categorized mail for **mentions of ASX tickers / paper holdings** and surface a bridge digest with links into Sender Inbox and company profiles.

## Demo

1. Run bridge scan over bounded ingested mail + active ASX set / paper positions  
2. See hits with deep links to sender + company profile  
3. False-positive controls (min token length, allowlist)  
4. No auto-trading; no auto-send  

## Committed

### S17.1 — Holdings-aware mail bridge (B83)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B83 |

**Acceptance criteria:**

- [ ] Bounded match of sender/subject/body keywords to ASX tickers / paper holdings
- [ ] Bridge results Markdown + deep links per UX
- [ ] False-positive controls documented
- [ ] Architecture note on matching approach
- [ ] No auto-trading; no auto-send

**Out of scope:** Broker statement scraping as primary path; silent portfolio changes
