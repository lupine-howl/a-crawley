# Roadmap

Ordered outcomes (not tasks). Product owner owns this file.  
**Working title:** Crawley  
**Code check (2026-07-16):** Sprints **6–24** shipped (OAuth ops + digests + notebook + VIP).  
**Retro:** [Sprints 1–5](docs/sprints/archive/sprints-1-5-retrospective.md)  
**Pivot:** **11**→**20** delivered. **21–24** delivered. **25–30** = remaining Email/ASX depth. Remaining former 31–40 / platform Later stays [shelved](docs/sprints/shelved/README.md).

## Now

**Shipped through Sprint 24:**

- [x] Shared Python core + stable module contract (confirm-first write-back for Calendar **and** Gmail send)
- [x] Local browser dashboard: themes, Settings, Markdown, home At a glance, Day brief
- [x] Investment + Gmail + Calendar (read); Calendar insert; Gmail confirm-first send
- [x] Fitness, Work, Co-parenting, DIY, Finance/Taxes, Coding/Creative lite modules
- [x] Opt-in phone-on-LAN; ADR-006 write-back model
- [x] LocalLlama (Ollama HTTP); shared context + history pins
- [x] Settings Update; Sender Inbox; ASX desk + paper + scale + events + bridge
- [x] ASX local alerts + recommendation feedback
- [x] Dual-desk operator playbooks + polish
- [x] Google OAuth ops (Tailscale Connect URI + softer consent)
- [x] Sender Inbox thread digests + VIP/muted rules
- [x] ASX research notebook / thesis

*Still out of Now:* native desktop wrapper, public hosting, multi-user, **live brokerage order placement**

## Next

**Depth band — Sprints 25–30** (active: Sprint 25)

### Sprint 25 (current) — ASX news theme clustering
Cluster headlines across active set into cited themes.  
[`docs/sprints/current.md`](docs/sprints/current.md) · B47

### Sprint 26 (planned) — Gmail labels confirm-first
Label apply/remove with ADR-006 audit.  
[`docs/sprints/planned/sprint-26-gmail-labels.md`](docs/sprints/planned/sprint-26-gmail-labels.md) · B48

### Sprint 27 (planned) — Manual holdings journal
Operator-entered holdings distinct from paper ledger.  
[`docs/sprints/planned/sprint-27-holdings-journal.md`](docs/sprints/planned/sprint-27-holdings-journal.md) · B49

### Sprint 28 (planned) — Gmail saved searches
Named bounded queries for skims/ingest.  
[`docs/sprints/planned/sprint-28-saved-searches.md`](docs/sprints/planned/sprint-28-saved-searches.md) · B50

### Sprint 29 (planned) — Gmail attachment skim
Metadata + opt-in bounded text extract.  
[`docs/sprints/planned/sprint-29-attachment-skim.md`](docs/sprints/planned/sprint-29-attachment-skim.md) · B52

### Sprint 30 (planned) — ASX citations + source quality
Structured citations and domain mute/quality tags.  
[`docs/sprints/planned/sprint-30-asx-citations.md`](docs/sprints/planned/sprint-30-asx-citations.md) · B53

### After Sprint 30

- Un-shelve selected former **31–40** / platform Later items where useful ([shelved](docs/sprints/shelved/README.md))
- Icebox stays closed without PRODUCT revision

## Closed

| Sprints | Theme | Evidence |
|---------|-------|----------|
| 1–5 | PoC shell → LAN | [archive](docs/sprints/archive/) |
| 6–10 | Life modules → shared context | [archive](docs/sprints/archive/sprint-6-10-life-modules-llm-context.md) |
| 11 | Settings Update | [archive](docs/sprints/archive/sprint-11-settings-update.md) |
| 12 | Sender Inbox | [archive](docs/sprints/archive/sprint-12-sender-inbox.md) |
| 13 | ASX desk | [archive](docs/sprints/archive/sprint-13-asx-profiles.md) |
| 14 | Paper + history + fitness | [archive](docs/sprints/archive/sprint-14-asx-paper-portfolio.md) |
| 15–17 | Scale + bridge | [archive](docs/sprints/archive/sprint-15-17-scale-bridge.md) |
| 18–20 | Send + alerts + playbooks | [archive](docs/sprints/archive/sprint-18-20-send-alerts-playbooks.md) |
| 21–24 | OAuth + digests + notebook + VIP | [archive](docs/sprints/archive/sprint-21-24-oauth-digests-notebook-vip.md) |
