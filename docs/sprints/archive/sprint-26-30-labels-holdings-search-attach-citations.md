# Sprints 26–30 — Labels, holdings, searches, attachments, citations

**Status:** closed  
**Duration:** five symbolic weeks  
**Backlog refs:** B48 (26); B49 (27); B50 (28); B52 (29); B53 (30)  
**Depends on:** ADR-006; Sprints 12–24  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**Previous:** [`archive/sprint-21-24-oauth-digests-notebook-vip.md`](sprint-21-24-oauth-digests-notebook-vip.md)  
**Next:** [`../current.md`](../current.md) (Sprint 25 — ASX news clustering, deferred during this bundle)  
**Note:** Sprint **25** (B47) was intentionally skipped and remains the next delivery.  
**Planned sources:**  
[`planned/sprint-26-gmail-labels.md`](../planned/sprint-26-gmail-labels.md) ·  
[`planned/sprint-27-holdings-journal.md`](../planned/sprint-27-holdings-journal.md) ·  
[`planned/sprint-28-saved-searches.md`](../planned/sprint-28-saved-searches.md) ·  
[`planned/sprint-29-attachment-skim.md`](../planned/sprint-29-attachment-skim.md) ·  
[`planned/sprint-30-asx-citations.md`](../planned/sprint-30-asx-citations.md)

## Goal

1. **Sprint 26:** Confirm-first Gmail label apply/remove + `gmail.modify` reconsent  
2. **Sprint 27:** Operator holdings journal (distinct from paper)  
3. **Sprint 28:** Named saved Gmail searches (bounded)  
4. **Sprint 29:** Attachment metadata + opt-in text extract  
5. **Sprint 30:** Structured citations + domain mute  

## Committed (done)

### S26.1 / B48 — Labels confirm-first — done
### S27.1 / B49 — Holdings journal — done
### S28.1 / B50 — Saved searches — done
### S29.1 / B52 — Attachment skim — done
### S30.1 / B53 — Citations & source quality — done

## Evidence

- `sender_inbox/labels.py` · `?gmail_modify=1` · ADR-006 amended  
- `asx_desk/holdings.py` · `/modules/investment/holdings`  
- `sender_inbox/saved_searches.py`  
- `sender_inbox/attachments.py` · digest slice hook  
- `asx_desk/citations.py` · profile `## Citations` · muted domains  
- `tests/test_sprints_26_30.py`
