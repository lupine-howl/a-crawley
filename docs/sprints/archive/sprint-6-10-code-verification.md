# Code verification — Sprints 6–10

**Date:** 2026-07-15  
**Conclusion:** Sprints **6–10 are implemented** in the current tree (not merely planned). Next delivery number is **Sprint 11**.

## Automated check

```text
uv run pytest tests/test_sprint6_10.py tests/test_sprint5.py -q
# 18 passed (2026-07-15 verification run)
```

## Module / feature map

| Claim (docs) | Code |
|--------------|------|
| Co-parenting lite | `src/crawley/modules/co_parenting.py` — registered in `registry.py` |
| DIY lite | `src/crawley/modules/diy.py` (+ `notes_lite.py`) |
| Finance lite | `src/crawley/modules/finance.py` |
| Day brief | `src/crawley/day_brief.py`; home section in `shell/templates/dashboard.html`; `/day-brief/refresh` |
| Calendar confirm-first insert | `src/crawley/modules/calendar.py` (`propose` / `confirm` / `events.insert`) |
| Write-back audit | `src/crawley/writeback.py`; Settings audit UI |
| LocalLlama / Ollama | `src/crawley/llm/local_llama.py`; ADR-007 |
| Coding/Creative lite | `src/crawley/modules/coding_creative.py` |
| Shared context | `src/crawley/shared_context.py`; ADR-008; standing notes on home |
| Registry complete | All nine top-tier modules live in `build_registry()` — no Coming-soon stubs for those ids |

## Doc correction note

An earlier pivot draft mistakenly labeled Sender Inbox work as “Sprint 6” and described sprints 6–40 as shelved. That was wrong numbering: **6–10 stay closed/delivered**; only the *former planned* post-10 queue is shelved; pivot is **Sprint 11–13**.
