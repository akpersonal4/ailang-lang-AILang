# Hypothesis Status

> Tracks the validation status of all engineering hypotheses defined in
> `VISION_AND_DIFFERENTIATION.md`. Every status change must reference
> benchmark evidence.

---

## Hypothesis Table

| # | Hypothesis | Status | Evidence | Last Updated |
|---|------------|--------|----------|-------------|
| H1 | Deterministic compilation makes debugging faster | **Partially Supported** | B3 Bug Fix: compiler errors catch bugs before runtime (80% first-fix compile rate). However, single-error-at-a-time reporting inflates fix iterations. | 2026-07-07 |
| H2 | Single canonical formatter eliminates code style discussions | **Not Yet Tested** | No benchmark measures style-related review time. Formatter exists and is idempotent (165/165 files). | 2026-07-07 |
| H3 | Specification-first design reduces documentation drift | **Supported** | M19 canonicalization eliminated 5 duplicate roadmap documents. Documentation Ownership Matrix prevents future drift. All docs validate against compiler. | 2026-07-07 |
| H4 | AI-friendly syntax reduces token consumption for LLM-based tools | **Inconclusive** | B7 AI Context shows structured guide saves 3× iterations. However, raw token consumption comparison (AILang vs Python) not measured. | 2026-07-07 |
| H5 | Integrated tooling reduces context-switching overhead | **Inconclusive** | B4 (Refactoring), B5 (Upgrade), B6 (Maintenance) show parity with Python (1.0× ratio), not improvement. The platform exists but hasn't been measured for cross-tool overhead reduction. | 2026-07-07 |
| H6 | Stdlib completeness reduces implementation iterations | **Supported** | v0.7.0: Adding `file.listdir`, fixing `convert.to_number`, adding `list.sum`/`list.find_by_key` reduced B2 L2 from 3→1 iterations (67% reduction). 42% of B2 errors were stdlib-related. | 2026-07-07 |
| H7 | AI context generation improves LLM output quality | **Supported** | B7 AI Context: structured guide (AGENTS.md + Playbook) reduces iterations from 3→1 (67% reduction). First-attempt compile rate improves from 0% to 100%. | 2026-07-07 |

---

## Detailed Status

### H1: Deterministic Compilation Helps Debugging

**Status:** Partially Supported

**Evidence:** B3 Bug Fix benchmark (5 scenarios):
- AILang first-fix compile rate: 80% (4/5 compiled on first fix)
- Python first-fix rate: 100% (5/5 worked on first attempt)
- Compiler errors prevented incorrect fixes from running (safe)
- But: AILang's single-error-at-a-time reporting required multiple iterations per fix

**Verdict:** Determinism helps correctness but not iteration count. The compiler acts as a safety net, not a speedup.

### H6: Stdlib Completeness Reduces Iterations

**Status:** Supported

**Evidence:** v0.7.0 Engineering Optimization:
- B2 L2 (CSV pipeline): 3 iterations → 1 iteration with `file.listdir`
- `convert.to_number` changed from no-op to actual converter
- `list.sum` and `list.find_by_key` reduce boilerplate
- 42% of B2 errors were stdlib-related (from ENGINEERING_EVIDENCE_REPORT.md)

### H7: AI Context Improves Output Quality

**Status:** Supported

**Evidence:** B7 AI Context benchmark:
- Without AGENTS.md guide: 3 iterations, 4 errors
- With AGENTS.md guide: 1 iteration, 0 errors
- 67% reduction in iterations
- Predictable errors (all covered by AGENTS.md §4 Hard Rules)

---

## Key Metrics

| Metric | Value |
|--------|-------|
| Total hypotheses defined | 7 |
| Supported | 3 (H3, H6, H7) |
| Partially Supported | 1 (H1) |
| Inconclusive | 2 (H4, H5) |
| Not Yet Tested | 1 (H2) |
| Rejected | 0 |
| Last updated | 2026-07-07 |
| Evidence source | ENGINEERING_EVIDENCE_REPORT.md |
