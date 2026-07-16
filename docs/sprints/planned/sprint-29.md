# Sprint 29 — Gmail attachments skim (bounded) (planned)

**Status:** shelved (superseded — active plan is [`sprint-29-attachment-skim.md`](sprint-29-attachment-skim.md) · B52 attachment skim)
**Duration:** one symbolic week  
**Backlog refs:** B52  
**Depends on:** B44, B27 helpful  
**Primary focus:** gmail  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**UX:** Prefer short `@ux-expert` pass when new Gmail chrome (lists, multi-select, rules) ships

## Goal

For selected messages/threads, list attachments and optionally extract **bounded text** from safe types for LLM context (PDFs/text) — privacy-minded, size-capped.

## Demo

1. See attachments on a thread
2. Opt-in extract text for small safe files
3. LLM can cite attachment titles/snippets

## Committed

### S29.1 — Attachment metadata + bounded extract (B52)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B52 |

**Acceptance criteria:**

- [ ] List attachment metadata (name, type, size) for selected message/thread
- [ ] Opt-in text extract for allowlisted types under size cap; store under data/
- [ ] Never auto-exfiltrate; clear skip reasons for unsafe/huge files
- [ ] Optional include snippets in digest prompt

---

**Out of scope (sprint):**

- Full antivirus product
- Preview of arbitrary binary formats
- Automated trading / order placement (Icebox)

## Parking lot

- Invoice/receipt structured extract (Finance bridge)
