# Sprint 19 — LAN gate + local backup/export (planned)

**Status:** shelved (deferred — Sender Inbox + ASX PoC pivot)  
**Duration:** one symbolic week  
**Backlog refs:** B40, B41  
**Depends on:** B12  
**UX:** Password/gate copy when LAN enabled; backup UX quiet

## Goal

Strengthen personal intrusion posture when LAN is on (**optional shared-secret gate**), and give a simple **local backup/export** of `data/` (minus needless secrets leakage controls documented).

## Demo

1. With LAN enabled, optional shared secret required to load UI (or documented equivalent gate)
2. Localhost path remains usable without friction (or documented exception)
3. Export/backup archive written locally; restore instructions documented

## Committed

### S19.1 — Optional LAN shared-secret gate (B40)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B40 |

**Acceptance criteria:**

- [ ] When LAN bind on, operator may enable a shared-secret (or basic gate)
- [ ] Trusted-LAN-only without gate remains available as explicit choice
- [ ] Documented in README + architecture; no public internet claims

### S19.2 — Local backup / export (B41)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B41 |

**Acceptance criteria:**

- [ ] Operator can export a bounded backup of app data locally
- [ ] Secrets handling documented (include vs exclude tokens; prefer explicit choice)
- [ ] No cloud upload feature

**Out of scope:** Enterprise SSO, remote backup SaaS
