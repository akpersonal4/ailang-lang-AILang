# M62 ROI Prioritization

**Date:** 2026-07-14
**Parent:** [M62 AI Correction Analysis](M62_AI_CORRECTION_ANALYSIS.md)

---

## 1. ROI Framework

**Expected Reduction (ER)** = Cycles eliminable × Time per cycle
**Implementation Cost (IC)** = Estimated LOC to implement
**ROI** = ER / IC

| Priority | ROI Score | Action |
|:--------:|:---------:|--------|
| 🔴 P0 | > 0.5 | Implement immediately |
| 🟡 P1 | 0.2–0.5 | Implement in next sprint |
| 🟢 P2 | 0.1–0.2 | backlog |
| ⚪ P3 | < 0.1 | Defer |

---

## 2. Proposed Fixes

### Fix 1: Pre-Flight Ordering Check (`ail check`)

**What:** A CLI command that checks forward references before compilation. Reports all ordering violations with exact locations.

| Metric | Value |
|--------|-------|
| **Target Category** | AICC-001 (Forward References) |
| **Cycles Eliminated** | 10 of 10 (100%) |
| **Time Saved** | 12 min |
| **Implementation Cost** | ~200 LOC (CLI tool using existing semantic analyzer) |
| **ER** | 10 cycles × 1.2 min = 12 min |
| **ROI** | 12 min / 200 LOC = 0.06 min/LOC |
| **Priority** | 🔴 P0 |

**Why P0:** Forward references are 38% of all AILang cycles. Every first compile fails. This is the single highest-impact fix.

**Implementation Approach:**
1. Add `cmd_check()` to `compiler/cli/main.py`
2. Reuse existing semantic analyzer to detect undefined identifiers
3. For each undefined identifier, search all imported modules for matching function definitions
4. Report: `FORWARD_REF: file.ail:line — '{fn}' is defined in {module}.ail but {module} is not yet imported or {fn} is defined after this call`
5. Suggest: `Move '{fn}' definition before this call, or import {module} at top of file`

**Existing Infrastructure:**
- Semantic analyzer already detects undefined identifiers (SEM002)
- Module import resolution already works
- Error reporting infrastructure exists (JSON + text)

---

### Fix 2: Map Constructor Helper (`map.from_pairs`)

**What:** A stdlib function that creates a map from key-value pairs in one call, eliminating sequential `map.set` calls.

| Metric | Value |
|--------|-------|
| **Target Category** | AICC-006 (Map Construction) |
| **Cycles Eliminated** | 2 of 3 (67%) |
| **Time Saved** | 2 min |
| **Implementation Cost** | ~40 LOC (builtin function) |
| **ER** | 2 cycles × 1.0 min = 2 min |
| **ROI** | 2 min / 40 LOC = 0.05 min/LOC |
| **Priority** | 🟡 P1 |

**Why P1:** Map construction is 12% of cycles but only 2 min total. High BRE if it also reduces boilerplate across all apps.

**Implementation:**
```
let m = map.from_pairs([["key1", "val1"], ["key2", "val2"]])
```

**Existing Infrastructure:**
- `map.new()` builtin exists
- `list.new()` + `list.append()` exist
- JSON parse already creates maps from arrays

---

### Fix 3: `ail test` Auto-Ordering

**What:** When `ail test` runs, automatically detect forward references in test files and suggest reordering.

| Metric | Value |
|--------|-------|
| **Target Category** | AICC-001 (partial — test files only) |
| **Cycles Eliminated** | 2 of 10 (20%) |
| **Time Saved** | 2.4 min |
| **Implementation Cost** | ~50 LOC (extend `ail test` with ordering check) |
| **ER** | 2 cycles × 1.2 min = 2.4 min |
| **ROI** | 2.4 min / 50 LOC = 0.048 min/LOC |
| **Priority** | 🟡 P1 |

**Why P1:** Complements Fix 1. Test files are the most common place where forward references occur because test functions call app functions.

**Implementation:**
- When `ail test` compiles a file, check for undefined identifiers
- If found, search the same file for matching function definitions
- Report: `Test file ordering: move '{fn}' definition before line {n}`

---

### Fix 4: Recursive Helper Template Generator

**What:** A CLI command that generates boilerplate for common recursive patterns (filter, map, find, reduce).

| Metric | Value |
|--------|-------|
| **Target Category** | AICC-005 (Recursive Helper) |
| **Cycles Eliminated** | 1 of 1 (100%) |
| **Time Saved** | 1 min |
| **Implementation Cost** | ~150 LOC (template generator) |
| **ER** | 1 cycle × 1.0 min = 1 min |
| **ROI** | 1 min / 150 LOC = 0.007 min/LOC |
| **Priority** | 🟢 P2 |

**Why P2:** Low cycle count (1), high implementation cost. But high LOC reduction if it eliminates boilerplate across all apps.

**Template Patterns:**
```
ail gen filter --field status --value open
ail gen map --field name --transform uppercase
ail gen find --field id --value 123
ail gen reduce --field total --operation sum
```

---

### Fix 5: `list.collect_key` Alias (`list.pluck`)

**What:** Add `list.pluck` as an alias for `list.collect_key` to match common AI terminology.

| Metric | Value |
|--------|-------|
| **Target Category** | AICC-004 (Missing Stdlib) |
| **Cycles Eliminated** | 1 of 2 (50%) |
| **Time Saved** | 1 min |
| **Implementation Cost** | ~10 LOC (wrapper function) |
| **ER** | 1 cycle × 2.0 min = 2 min |
| **ROI** | 2 min / 10 LOC = 0.2 min/LOC |
| **Priority** | 🟡 P1 |

**Why P1:** Very low cost, high ROI. AI models often use "pluck" terminology.

---

### Fix 6: `string.concat` Variadic Support

**What:** Allow `string.concat` to take 2+ arguments instead of exactly 2.

| Metric | Value |
|--------|-------|
| **Target Category** | AICC-004 (Missing Stdlib) |
| **Cycles Eliminated** | 0 of 2 (0%) |
| **Time Saved** | 0 min |
| **Implementation Cost** | ~30 LOC (modify builtin) |
| **ER** | 0 min |
| **ROI** | 0 min / 30 LOC = 0 |
| **Priority** | ⚪ P3 |

**Why P3:** The existing `+` operator already handles 3+ strings. This is a convenience feature, not a cycle reducer.

---

## 3. Prioritized Roadmap

### Phase 1: Highest Impact (P0)

| Fix | Cycles Saved | Time Saved | LOC | ROI |
|-----|:-----------:|:----------:|:---:|:---:|
| Fix 1: Pre-flight ordering check | 10 | 12 min | 200 | 0.06 |
| **Phase 1 Total** | **10** | **12 min** | **200** | **0.06** |

**Result:** AILang correction cycles drop from 26 to 16 (38% reduction). AILang becomes 30% more efficient than Python (16 vs 23).

### Phase 2: Stdlib & Tooling (P1)

| Fix | Cycles Saved | Time Saved | LOC | ROI |
|-----|:-----------:|:----------:|:---:|:---:|
| Fix 2: Map constructor helper | 2 | 2 min | 40 | 0.05 |
| Fix 3: `ail test` auto-ordering | 2 | 2.4 min | 50 | 0.048 |
| Fix 5: `list.pluck` alias | 1 | 1 min | 10 | 0.2 |
| **Phase 2 Total** | **5** | **5.4 min** | **100** | **0.054** |

**Result:** AILang correction cycles drop from 16 to 11 (58% reduction from original). AILang becomes 52% more efficient than Python (11 vs 23).

### Phase 3: Developer Experience (P2)

| Fix | Cycles Saved | Time Saved | LOC | ROI |
|-----|:-----------:|:----------:|:---:|:---:|
| Fix 4: Recursive helper templates | 1 | 1 min | 150 | 0.007 |
| **Phase 3 Total** | **1** | **1 min** | **150** | **0.007** |

**Result:** AILang correction cycles drop from 11 to 10 (62% reduction from original). AILang becomes 57% more efficient than Python (10 vs 23).

---

## 4. Cumulative Impact

| Metric | Before | After Phase 1 | After Phase 2 | After Phase 3 |
|--------|:------:|:-------------:|:-------------:|:-------------:|
| AILang cycles | 26 | 16 | 11 | 10 |
| Python cycles | 23 | 23 | 23 | 23 |
| AILang/Python ratio | 1.13× | 0.70× | 0.48× | 0.43× |
| AILang time | 32 min | 20 min | 14.6 min | 13.6 min |
| Python time | 27 min | 27 min | 27 min | 27 min |
| AILang/Python time ratio | 1.19× | 0.74× | 0.54× | 0.50× |

**After all phases, AILang requires 57% fewer correction cycles and 50% less correction time than Python.**

---

## 5. Implementation Dependencies

| Fix | Depends On | Blocks |
|-----|------------|--------|
| Fix 1 | None | Fix 3 |
| Fix 2 | None | None |
| Fix 3 | Fix 1 | None |
| Fix 4 | None | None |
| Fix 5 | None | None |
| Fix 6 | None | None |

**Critical path:** Fix 1 → Fix 3 (sequential)
**Parallel work:** Fix 2, Fix 4, Fix 5, Fix 6 (independent)

---

## 6. Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Fix 1 false positives | Medium | Use existing SEM002 infrastructure (proven accurate) |
| Fix 2 breaking changes | Low | Additive only — no existing code affected |
| Fix 3 limited to test files | Low | Already covers 20% of forward ref cycles |
| Fix 4 template complexity | Medium | Start with 4 most common patterns |
| Fix 5 naming confusion | Low | Alias is optional — existing API unchanged |

---

## 7. Related Documents

- [M62 AI Correction Analysis](M62_AI_CORRECTION_ANALYSIS.md) — Full analysis
- [M62 Root Cause Table](M62_ROOT_CAUSE_TABLE.md) — Every cycle classified
- [M62 Recommendations](M62_RECOMMENDATIONS.md) — Concrete next steps
- [P0 Boilerplate Reduction Plan](../roadmap/P0_BOILERPLATE_REDUCTION_PLAN.md) — Measured BRE metrics
