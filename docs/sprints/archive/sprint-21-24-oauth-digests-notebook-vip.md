# Sprints 21–24 — OAuth ops + digests + notebook + VIP

**Status:** closed  
**Duration:** four symbolic weeks  
**Backlog refs:** B89–B90 (21); B44 (22); B45 (23); B46 (24)  
**Depends on:** Sprints 12–20 dual-desk stack  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**Previous:** [`archive/sprint-18-20-send-alerts-playbooks.md`](sprint-18-20-send-alerts-playbooks.md)  
**Next:** [`../current.md`](../current.md) (Sprint 25 — ASX news theme clustering)  
**Planned sources:**  
[`planned/sprint-21-google-oauth-ops.md`](../planned/sprint-21-google-oauth-ops.md) ·  
[`planned/sprint-22-thread-digests.md`](../planned/sprint-22-thread-digests.md) ·  
[`planned/sprint-23-asx-notebook.md`](../planned/sprint-23-asx-notebook.md) ·  
[`planned/sprint-24-sender-vip-rules.md`](../planned/sprint-24-sender-vip-rules.md)

## Goal

1. **Sprint 21:** Tailscale/LAN Connect URI + softer OAuth consent.  
2. **Sprint 22:** Bounded Sender Inbox thread digests.  
3. **Sprint 23:** ASX per-ticker research notebook seeding LLM runs.  
4. **Sprint 24:** Local VIP / muted sender rules.

## Demo

1. Settings / Connect show copyable Host redirect URI; reconnect without forced consent when refresh + scopes present  
2. Sender detail → Digest thread → Markdown (summary / asks / commitments)  
3. ASX company → Save notebook → regenerate profile uses capped slice  
4. Mark VIP/muted → list order + categorization honor rules  

## Committed (done)

### S21.1 — Tailscale / LAN first-Connect ergonomics (B89) — done
### S21.2 — Softer OAuth consent prompts (B90) — done
### S22.1 — Thread digest from Sender Inbox (B44) — done
### S23.1 — ASX thesis & notebook (B45) — done
### S24.1 — Local sender priority rules (B46) — done

## Explicitly out of sprint

- Multi-user Google / public HTTPS
- Google filter sync
- Full mailbox index / silent auto-replies
- Brokerage sync / automated trading
- Sprints 25–30 depth items

## Evidence

- `src/crawley/google_oauth.py` — `should_force_consent`, conditional `prompt=consent`
- Settings `#google` + Connect panels — copyable redirect URI
- `sender_inbox/digests.py` + `fetch_thread_messages`
- `asx_desk/notebook.py` + company profile UI
- `sender_inbox/rules.py` — VIP/muted CRUD + list/categorize hooks
- `tests/test_sprints_21_24.py`
