# Sprint 25 — ASX news theme clustering

**Status:** closed  
**Duration:** one symbolic week  
**Backlog refs:** B47  
**Depends on:** Sprint 13–16 ASX desk; Sprint 30 citations (muted domains) helpful  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**Previous:** [`archive/sprint-21-24-oauth-digests-notebook-vip.md`](sprint-21-24-oauth-digests-notebook-vip.md) · [`archive/sprint-26-30-labels-holdings-search-attach-citations.md`](sprint-26-30-labels-holdings-search-attach-citations.md)  
**Planned source:** [`planned/sprint-25-asx-news-clusters.md`](../planned/sprint-25-asx-news-clusters.md)

## Goal

Cluster bounded news/headlines across the active ASX set into cited **themes** — research aid, not trade signals.

## Demo

1. Investment → **Themes** → Cluster headlines  
2. Themes with source lists; empty/error honest  
3. No trade buttons  

## Committed (done)

### S25.1 — Active-set news clustering (B47) — done

- Bounded reuse of scan headlines (≤80, ≤4/ticker); muted domains excluded  
- LLM clustering when available; keyword heuristic fallback  
- Panel at `/modules/investment/clusters`; hard caps; non-order copy  

## Evidence

- `src/crawley/asx_desk/clusters.py`  
- Template `asx_clusters.html` · subnav **Themes**  
- `tests/test_sprint_25.py`
