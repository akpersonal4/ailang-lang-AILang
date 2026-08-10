# A100 Participant Data-Collection Form

**This form captures the exact metrics defined in `docs/roadmap/A100_COMMUNITY_VALIDATION.md`.**
Fill in one copy per participant per language run (Python and AILang). Keep the
event log terse — timestamps, action, outcome. The two choice questions are
answered once per participant at the very end of the study.

---

## A. Run identity

| Field | Value |
|-------|-------|
| Participant ID | P__ |
| Run order (Python-first / AILang-first) |  |
| Language this form covers | Python / AILang |
| AILang version (`ail --version`) |  |
| Python version |  |
| AI tool/model used |  |
| Date |  |

---

## B. Phase 1 — Greenfield

### B.1 Metrics

| Metric | Value |
|--------|-------|
| Time to first working version (minutes) |  |
| AI correction iterations (times you asked the AI to fix/redo work) |  |
| Compiler errors (AILang) / runtime exceptions (Python) count |  |
| Frustration rating (1 = smooth, 5 = very frustrating) |  |

### B.2 Event log

| Time | Action | Outcome |
|------|--------|---------|
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |

---

## C. Phase 2 — Maintenance

### C.1 Per-change metrics

| Change | Time (min) | AI correction iterations | Compiler errors / runtime exceptions | Bugs introduced (Y/N + which) |
|--------|-----------|--------------------------|--------------------------------------|-------------------------------|
| M1 GST |  |  |  |  |
| M2 Discounts |  |  |  |  |
| M3 Currency column |  |  |  |  |
| M4 Role-based permissions |  |  |  |  |
| M5 Per-category tax |  |  |  |  |
| M6 Approval workflow |  |  |  |  |

### C.2 Phase-level metrics

| Metric | Value |
|--------|-------|
| Total maintenance time (minutes) |  |
| Change requests completed (1–6) |  |
| Confidence rating code is correct/complete (1 = low, 5 = high) |  |

### C.3 Event log

| Time | Change | Action | Outcome |
|------|--------|--------|---------|
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |

---

## D. First-impression bugs / observations (found during runs)

Record every environment or tool defect noticed, exactly as seen (do not fix
silently — log it):

| Language | Defect | Impact | Severity (blocking / minor / cosmetic) |
|----------|--------|--------|----------------------------------------|
|  |  |  |  |
|  |  |  |  |

> Note for coordinator: any defect that blocks a participant from reaching
> "first working version" in the AILang run of published v1.1.17 counts against
> the "0 release-blocking defects" success criterion — classify carefully.

---

## E. Feature requests / missing-tooling notes (no implementation during study)

| Language | Request | Context (what you were doing) |
|----------|---------|-------------------------------|
|  |  |  |
|  |  |  |

---

## F. Choice questions (answer ONCE, after both languages' M6 complete)

1. **Which was easier?** (Python / AILang / about equal)

   Comment:

2. **Which would you choose for your next project of the same kind?** (Python / AILang)

   Comment:
