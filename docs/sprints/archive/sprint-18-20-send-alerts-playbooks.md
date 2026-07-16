# Sprints 18–20 — Gmail send, ASX alerts, playbooks

**Status:** closed  
**Duration:** three symbolic weeks  
**Backlog refs:** B84 (18); B85–B86 (19); B87–B88 (20)  
**Depends on:** ADR-006; Sprints 12–17 dual desks  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**Previous:** [`archive/sprint-15-17-scale-bridge.md`](sprint-15-17-scale-bridge.md)  
**Next:** [`../current.md`](../current.md) (Sprint 21 — Google OAuth ops)  
**Planned sources:** [`planned/sprint-18-gmail-send.md`](../planned/sprint-18-gmail-send.md) · [`planned/sprint-19-asx-alerts.md`](../planned/sprint-19-asx-alerts.md) · [`planned/sprint-20-playbooks-polish.md`](../planned/sprint-20-playbooks-polish.md)

## Goal

1. **Sprint 18:** Confirm-first Gmail send with audit + opt-in `gmail.send` scope.  
2. **Sprint 19:** Local ASX alerts + recommendation accept/dismiss/snooze feedback.  
3. **Sprint 20:** Operator playbooks + dual-desk polish.

## Demo

1. Propose reply from Sender detail → Cancel (no send) / Confirm (send + audit)  
2. Add alert rule; evaluate after scan; dismiss/snooze recommendation  
3. Run “ASX scan + refresh recs” playbook from Settings or desk  

## PO polish list (S20.2 — recorded before implement)

1. Clearer empty states on ASX desk / recommendations when active set or rows empty  
2. Home chip for open ASX alerts  
3. Playbook entry points on both desks + Settings  
4. Sender detail copy: todos local; compose is the send path  
5. Alerts labelled informational-only (no trades)

## Committed

### S18.1 — Gmail confirm-first send (B84) · done
### S19.1 — Local ASX alerts (B85) · done
### S19.2 — Recommendation feedback loop (B86) · done
### S20.1 — Operator playbooks (B87) · done
### S20.2 — Dual-desk polish pass (B88) · done

## Explicitly out of sprint

- Bulk send; SMS/email push; live brokerage  
- Full redesign; desktop shell  

## Parking lot

- Scheduled overnight playbooks  
- Undo send from audit  
