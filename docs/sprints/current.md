# Sprint 21 — Google OAuth ops (Tailscale Connect + softer reconsent)

**Status:** ready (next delivery; Sprints 18–20 archived)  
**Duration:** one symbolic week  
**Backlog refs:** B89, B90  
**Depends on:** B15 shared Google OAuth; LAN/Tailscale bind (B12)  
**Architecture:** [`docs/architecture.md`](../architecture.md) — installed-app OAuth; tokens in `data/secrets/`  
**UX:** Minimal — Settings / Connect panel copy for redirect URI; no new desk  
**Previous:** [`archive/sprint-18-20-send-alerts-playbooks.md`](archive/sprint-18-20-send-alerts-playbooks.md)  
**Planned source:** [`planned/sprint-21-google-oauth-ops.md`](planned/sprint-21-google-oauth-ops.md)

## Goal

Make **first Connect Google** reliable from a Tailscale (or trusted LAN) client, and reduce unnecessary re-authentication prompts while keeping offline refresh tokens and explicit reconsent when scopes change.

## Demo

1. From a Tailscale/LAN client: open Crawley → see the exact redirect URI → Connect succeeds → token on server  
2. Reconnect with already-granted scopes does **not** force full consent unless refresh token missing or new scopes requested  
3. README documents Testing-mode ~7-day refresh expiry vs Production, and WSL/Tailscale same-environment tip

## Committed

Implement **in order** (S21.1 → S21.2).

### S21.1 — Tailscale / LAN first-Connect ergonomics (B89)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B89 |

**Acceptance criteria:**

- [ ] When operator opens Connect from a trusted personal host (Tailscale / LAN), UI shows the **exact** OAuth redirect URI for that request Host (copyable)
- [ ] README (or Settings Network + Google section) covers: add that URI in Google Cloud; Tailscale in same env as Crawley; token reuse across clients of one server
- [ ] Existing localhost Connect path unchanged
- [ ] Automated test covers redirect URI construction for a Tailscale-like Host header (or trusted-host helper)

### S21.2 — Softer OAuth consent prompts (B90)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B90 |

**Acceptance criteria:**

- [ ] `authorization_url` no longer always forces `prompt=consent`; force consent only when refresh token is missing **or** requesting scopes not already granted (e.g. Calendar write / Gmail send upgrade)
- [ ] `access_type=offline` retained so refresh tokens still issued on first grant
- [ ] Normal API use still auto-refreshes via `load_credentials` without UI prompts
- [ ] README notes Google **Testing** publishing status (~7-day refresh token expiry) vs Production as the main “weekly re-auth” cause
- [ ] Tests cover consent-forced vs consent-optional paths

## Explicitly out of sprint

- Multi-user Google accounts / per-client tokens
- Public HTTPS / reverse-proxy productization
- Unshelving B44+ depth (Sprints 22+)
- Icebox (live brokerage)

## Parking lot

- Optional “copy redirect URI” on Settings even before Connect
- MagicDNS vs 100.x IP: document both if both used
