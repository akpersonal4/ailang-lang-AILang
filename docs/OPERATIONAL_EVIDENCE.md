# Operational Evidence Collection

## Metrics Tracking

| Metric | Current Value | Target | Notes |
|--------|---------------|--------|-------|
| Features added / month | 0 | 2 | Increment when new AILang features are merged |
| Bugs found / month | 0 | 3 | Record each reported bug |
| Mean fix time (minutes) | 0 | 15 | Average time from bug report to commit |
| Compile‑time detections | 0 | 12 | Number of compile‑time errors caught per month |
| Runtime failures | 0 | 1 | Count of crashes / unhandled exceptions during runs |
| Refactors using `ail rename` | 0 | 4 | Manual count of rename operations performed via the tool |
| Backup restores | 0 | 0 | Number of successful data restores from backups |
| Production incidents | 0 | 0 | Critical incidents affecting live usage |

## Milestone: M40 — Operational Validation

**Goal:** Run the inventory application continuously for **90 days**.

**Success criteria:**
- No data loss
- No unrecoverable corruption
- No production‑stopping bug
- Mean fix time < 1 hour
- Users would choose AILang again

If these conditions hold, the project can be promoted to **v1.0.0** (full release, no longer a release candidate).

---

*Update this file regularly as metrics are observed.*