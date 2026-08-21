# AILang A101 — Engineering Hardening Plan

> **Status:** PLANNING ONLY — No code, no fixes, no version changes
>
> **Source:** A100 Consolidated Report + A101 Finding Reconciliation + ADR-017 + V2 Strategic Plan
>
> **Date:** 2026-08-20
>
> **Authorization required:** Project owner must approve this plan before any implementation begins.

---

## 1. Business-Readiness Contract

### 1.1 SIMPLE

| Criterion | Current Evidence | Verdict | Remaining Gap | Measurement Required | Acceptance Threshold |
|-----------|-----------------|---------|---------------|---------------------|---------------------|
| Install to first program | Dev1: <5 min, first attempt | PASS | None | None | <5 min, first attempt |
| Onboarding docs complete | All 5: positive | PASS | None | None | All evaluators rate >=4/5 |
| Greenfield app from spec | Dev1,3,4: 1 iteration; Dev2: 2 iterations | PASS | None | None | <=2 iterations to working |
| No opaque internal errors | Dev1: CMP001 on environment.args | FAIL | F-07 | Fix error message | Zero internal errors on valid user mistakes |
| No silent statement drops | Dev1: let x = silently ignored | FAIL | F-08 | Fix parser | Parser errors on incomplete statements |

**Overall SIMPLE verdict: PARTIAL → will become PASS after F-07, F-08 fixes**

### 1.2 FAST

| Criterion | Current Evidence | Verdict | Remaining Gap | Measurement Required | Acceptance Threshold |
|-----------|-----------------|---------|---------------|---------------------|---------------------|
| Compile <500ms | Dev1-5: ~330-530ms | PARTIAL | High end exceeds 500ms | Profile compile hotspots | 95th percentile <500ms |
| Canonical 10k <5s | ADR-017: 980ms; Dev4: 13.5s | PARTIAL | Complex workloads exceed target | Benchmark canonical workload | Mean <5s on canonical |
| Linear scaling | Dev1: linear with batching; Dev4: superlinear | PARTIAL | List/map recursion causes superlinear | Profile per-call overhead | <2x overhead vs linear |
| No unnecessary compile overhead | Dev4: 514ms compile at N=100 (85% of total) | FAIL | Compile dominates small runs | Profile compile path | Compile <200ms for small programs |

**Overall FAST verdict: PARTIAL — workload-dependent, not universally fast**

### 1.3 RELIABLE

| Criterion | Current Evidence | Verdict | Remaining Gap | Measurement Required | Acceptance Threshold |
|-----------|-----------------|---------|---------------|---------------------|---------------------|
| Byte-identical determinism | All 5: 5/5 runs identical | PASS | None | None | 5/5 identical on 3+ workloads |
| Correct exit codes | All 5: consistent | PASS | None | None | Exit code matches program outcome |
| Safe external input | Dev2,4,5: crash on malformed data | FAIL | F-02: no try/catch | Add safe parse | Zero crashes on malformed input |
| No interpreter crashes | Dev1: hangman crash 2/17 | FAIL | F-09: bundled app crash | Fix app | Zero interpreter crashes on shipped apps |
| Money-safe arithmetic | All 5: correct with integer-cents | PARTIAL | F-01: no float parsing | Add convert.to_float() | Decimal strings parse correctly |

**Overall RELIABLE verdict: PARTIAL — determinism is strong, but error handling is absent**

### 1.4 AI-MAINTAINABLE

| Criterion | Current Evidence | Verdict | Remaining Gap | Measurement Required | Acceptance Threshold |
|-----------|-----------------|---------|---------------|---------------------|---------------------|
| Spec-to-code accuracy | All 5: code matches spec | PASS | None | None | >=90% first-pass accuracy |
| Change accuracy | All 5: maintenance 1-2 iterations | PASS | None | None | >=90% first-pass success |
| Determinism enables verification | All 5: byte-identical | PASS | None | None | Byte-identical across runs |
| Structured diagnostics | Dev1,4: excellent | PASS | None | None | All errors have location + suggestion |
| AI can handle recursion limits | Dev1: batching workaround | PARTIAL | F-14: limits undocumented | Document limits | AI knows about 2000 limit |

**Overall AI-MAINTAINABLE verdict: PASS — strongest pillar**

### 1.5 EASY-TO-EXTEND

| Criterion | Current Evidence | Verdict | Remaining Gap | Measurement Required | Acceptance Threshold |
|-----------|-----------------|---------|---------------|---------------------|---------------------|
| Guard discipline | All 5: map.has before map.get | PASS | None | None | Pattern consistently teachable |
| Bottom-up ordering | 4/5: friction observed | PARTIAL | F-24: ordering friction | Accept (ADR-004) | Workable with tooling support |
| No forward references | All 5: enforced | PASS | None | None | Compiler catches all violations |
| Module system works | Dev1,2: multi-file apps work | PARTIAL | F-11: error misattribution | Defer | Errors at correct source location |

**Overall EASY-TO-EXTEND verdict: PARTIAL — ordering friction is a known trade-off**

---

## 2. Architecture Gate Decision

### 2.1 V2 Escalation Framework Applied

Per V2 section 1.5, architecture escalation fires when ALL THREE conditions are met:

| Condition | Required | Current Evidence | Met? |
|-----------|----------|-----------------|------|
| (1) Canonical 10k exceeds target | >5s on canonical workload | ADR-017: 980ms (PASS); Dev4: 13.5s (FAIL on complex workload) | PARTIALLY |
| (2) >=50% runtime is dispatch overhead | cProfile shows dispatch >50% | ADR-017 Phase 2: 24.2% | NO |
| (3) Gate A/B options exhausted | All incremental optimizations tried | Zero optimizations attempted | NO |

**Verdict: ARCHITECTURE CONTINUE**

Condition (2) is definitively NOT met. Dispatch overhead is 24.2%, well below the 50% threshold. Condition (3) is NOT met — no optimization has been attempted. Even though condition (1) is partially met for complex workloads, the other two conditions prevent escalation.

### 2.2 Root Cause of Performance Gap

The performance gap is NOT caused by interpreter dispatch. It is caused by:

1. **Per-call overhead in list/map recursion** — each recursive call over a list involves function-call overhead, name resolution, and argument evaluation. With no native map/filter/reduce, every pass is a full recursive call chain.
2. **Compile overhead** — ~330-530ms constant, dominates small workloads.
3. **Recursion constraints** — list/map recursion hits 2000-frame limit, forcing batching workarounds that add overhead.

These are NOT architecture problems. They are:
- (1) A stdlib gap (no native list operations)
- (2) A compiler optimization opportunity
- (3) A recursion model constraint (documented in ADR-017)

### 2.3 Recommended Architecture Action

**No architecture escalation.** Instead:

1. **Gate A investigation (optional):** Profile the canonical 10k workload to identify whether native list.map / list.filter / list.reduce would meaningfully improve performance. If yes, add as P2 stdlib enhancement.
2. **Document recursion constraints:** Make the 2000-frame limit and batching workaround visible to developers.
3. **Do NOT pursue VM/bytecode:** The evidence does not justify it. Dispatch is 24.2%, not 50%+.

---

## 3. A101 Hardening Plan

### Phase 0 — Evidence / Reproduction (1-2 days)

**Goal:** Confirm or reject unconfirmed findings before planning fixes.

| Task | Finding | What to do | Acceptance criteria |
|------|---------|-----------|---------------------|
| Reproduce cumulative recursion budget | F-04 | Create controlled test: single main() with 3 recursive passes over N records. Vary N from 100 to 1000. Measure where failure occurs. | Confirm or reject Dev2's 500-600 record threshold |
| Reproduce hangman crash rate | F-09 | Run bundled hangman 100 times. Count crashes. | Confirm or reject ~12% crash rate |
| Test malformed CSV behavior | 3.3 conflict | Test 5 malformation types: missing fields, unclosed quotes, wrong column count, non-numeric in numeric field, empty file. Record behavior for each. | Document exact behavior per malformation type |
| Test recursion error message | 3.2 conflict | Trigger both depth limit (2000) and cumulative budget (100k). Compare error messages. | Confirm whether error always says "limit: 2000" |

**Exit criteria:** All unconfirmed findings either confirmed or rejected. Confirmed findings have exact reproduction steps.

---

### Phase 1 — P0 Fixes (3-5 days)

**Goal:** Address the four P0 blockers that prevent business-readiness claims.

#### 1A: Add convert.try_to_int() and convert.try_to_float()

| Field | Value |
|-------|-------|
| **Problem** | No way to parse numeric strings without crashing on bad input |
| **Why it matters** | Blocks V2 P0-3 money contract; blocks safe external input processing |
| **Evidence** | F-01 (5/5 evaluators), F-02 (3/5 evaluators) |
| **Scope** | Add two new builtin functions to compiler/runtime/builtins.py |
| **Files likely affected** | compiler/runtime/builtins.py, docs/reference/STDLIB_REFERENCE.md |
| **Compatibility risk** | None — additive only, no existing API changes |
| **Test strategy** | Add tests for: valid int, valid float, invalid string, empty string, null. Verify return values (number or sentinel). |
| **Acceptance criteria** | convert.try_to_int("12.50") returns 12.50 (or 12 if int). convert.try_to_int("abc") returns sentinel (not crash). convert.try_to_float("3.5") returns 3.5. All existing tests pass. |
| **Rollback strategy** | Remove the two new functions. No other code depends on them. |
| **Architecture impact** | None — stdlib addition only |
| **Release impact** | Minor version bump (new API surface) |

#### 1B: Add convert.to_float()

| Field | Value |
|-------|-------|
| **Problem** | No way to parse decimal strings at all |
| **Why it matters** | Financial applications need decimal parsing |
| **Evidence** | F-01 (5/5 evaluators) |
| **Scope** | Add convert.to_float() builtin |
| **Files likely affected** | compiler/runtime/builtins.py, docs |
| **Compatibility risk** | None — additive |
| **Test strategy** | Valid float, valid int-as-float, invalid string raises RuntimeError |
| **Acceptance criteria** | convert.to_float("12.50") returns 12.5. convert.to_float("abc") raises. |
| **Rollback** | Remove function |
| **Architecture impact** | None |

#### 1C: Document Recursion Constraints

| Field | Value |
|-------|-------|
| **Problem** | 2000-frame limit not documented; developers hit it cold |
| **Why it matters** | F-14: 3/5 evaluators hit undocumented limit |
| **Evidence** | F-14 |
| **Scope** | Update GETTING_STARTED, LANGUAGE_SPEC, create troubleshooting entry |
| **Files likely affected** | docs/guides/GETTING_STARTED.md, docs/reference/LANGUAGE_SPEC.md |
| **Compatibility risk** | None — documentation only |
| **Test strategy** | Verify docs contain limit info and batching workaround |
| **Acceptance criteria** | New developer learns about 2000 limit before hitting it |
| **Architecture impact** | None |

#### 1D: Fix Bundled Hangman App

| Field | Value |
|-------|-------|
| **Problem** | Bundled app crashes interpreter silently ~12% of runs |
| **Why it matters** | F-09: shipped app quality signal |
| **Evidence** | F-09 |
| **Scope** | Fix pick_guess() to filter alphabet; fix eveal_random() to handle all-guessed |
| **Files likely affected** | il_platform/data/apps/hangman_game/main.ail |
| **Compatibility risk** | None — app fix only |
| **Test strategy** | Run 20 times, verify 0 crashes |
| **Acceptance criteria** | 20/20 runs complete with exit 0 |
| **Architecture impact** | None |

**Phase 1 exit criteria:** All 4 P0 fixes implemented, all existing tests pass, new tests pass, docs updated.

---

### Phase 2 — P1 Fixes (3-5 days)

**Goal:** Address findings that should be fixed before claiming business-ready.

#### 2A: Add // Expression Warning

| Field | Value |
|-------|-------|
| **Problem** |  // b silently becomes  (comment trap) |
| **Why it matters** | F-05: silent wrong answers for Python/C/Java/JS developers |
| **Evidence** | F-05 |
| **Scope** | Add compiler warning when // appears in expression context |
| **Files likely affected** | compiler/semantic/, compiler/interpreter/ |
| **Compatibility risk** | Low — warning only, no behavior change |
| **Test strategy** | Verify 10 // 3 emits warning but still evaluates to 10 |
| **Acceptance criteria** | Warning emitted for  // b in expressions; no warning for // at line start (actual comments) |
| **Architecture impact** | None |

#### 2B: Fix environment.args Error Message

| Field | Value |
|-------|-------|
| **Problem** | environment.args without parens triggers internal CMP001 error |
| **Why it matters** | F-07: opaque error on common mistake |
| **Evidence** | F-07 |
| **Scope** | Add diagnostic: "Did you mean environment.args()?" |
| **Files likely affected** | Compiler error handling |
| **Compatibility risk** | None — improved error message only |
| **Test strategy** | Verify environment.args (no parens) produces helpful error, not CMP001 |
| **Acceptance criteria** | Error message suggests adding parentheses |
| **Architecture impact** | None |

#### 2C: Fix Incomplete Statement Parser

| Field | Value |
|-------|-------|
| **Problem** | let x = silently ignored |
| **Why it matters** | F-08: silent non-execution |
| **Evidence** | F-08 |
| **Scope** | Parser should error on incomplete let assignment |
| **Files likely affected** | Parser |
| **Compatibility risk** | Low — currently silent, will now error |
| **Test strategy** | Verify let x = produces parse error |
| **Acceptance criteria** | Parser rejects incomplete let with helpful message |
| **Architecture impact** | None |

#### 2D: Improve Test Runner

| Field | Value |
|-------|-------|
| **Problem** | File-level reporting; first-failure abort |
| **Why it matters** | F-06: 4/5 evaluators found test reporting inadequate |
| **Evidence** | F-06 |
| **Scope** | Per-function reporting + --continue-on-fail option |
| **Files likely affected** | compiler/cmd_test.py or equivalent |
| **Compatibility risk** | Medium — changes test output format |
| **Test strategy** | Verify per-function counts; verify --continue-on-fail runs all tests |
| **Acceptance criteria** | "3/5 tests passed" (functions, not files); --continue-on-fail reports all failures |
| **Architecture impact** | None |

#### 2E: Fix Pass-by-Value Documentation

| Field | Value |
|-------|-------|
| **Problem** | Recursion accumulator pattern not documented |
| **Why it matters** | F-10: silent wrong answers for imperative-background devs |
| **Evidence** | F-10 |
| **Scope** | Add accumulator patterns section to GETTING_STARTED |
| **Files likely affected** | docs/guides/GETTING_STARTED.md |
| **Compatibility risk** | None |
| **Test strategy** | Verify docs contain accumulator guidance |
| **Acceptance criteria** | Developer learns to return accumulators from recursive calls |
| **Architecture impact** | None |

**Phase 2 exit criteria:** All P1 fixes implemented, all tests pass, docs updated.

---

### Phase 3 — P2 Improvements (5-10 days)

**Goal:** Address important improvements that enhance developer experience.

| Task | Finding | Scope | Effort |
|------|---------|-------|--------|
| Fix list.sort docs | F-17 | Correct contradiction in STDLIB_REFERENCE | Low |
| Clarify convert.to_number | F-16 | Document as alias for 	o_int in STDLIB_REFERENCE | Low |
| Fix environment.args doc | F-18 | Add function-call syntax signal to table entry | Low |
| Document string.split newline behavior | F-12 | Note in STDLIB_REFERENCE; consider string.split_lines() | Low |
| Mark static_analyzer incomplete | F-13 | Add "experimental" label or remove from stdlib | Low |
| Document accumulator patterns | F-10 | Add to GETTING_STARTED | Low |
| Improve error source tracking | F-11 | Report errors at actual source location in imported modules | Medium |
| Consider // integer division | F-05 | If warning (Phase 2) is insufficient, consider math.div promotion | Low |

---

### Phase 4 — Documentation / Tooling (2-3 days)

**Goal:** Close all documentation gaps.

| Task | Finding | Scope |
|------|---------|-------|
| Document BOM rejection | F-15 | Add "save as UTF-8 without BOM" to GETTING_STARTED |
| Fix SEM001 wording | F-19 | Refine error message to match actual behavior |
| Document string.substring | F-20 | Clarify start/end semantics in STDLIB_REFERENCE |
| Fix semicolon documentation | F-21 | Update LANGUAGE_SPEC to match behavior (optional) |
| Document #/
ot/nested functions | F-23 | Add Python-convert friction notes to GETTING_STARTED |
| Create troubleshooting guide | Multiple | Common pitfalls: // trap, BOM, bottom-up ordering, recursion limit |

---

### Phase 5 — Revalidation (2-3 days)

**Goal:** Verify all fixes work and no regressions introduced.

| Task | What | Acceptance criteria |
|------|------|---------------------|
| Run full test suite | il test on all existing tests | 100% pass rate |
| Run A100 protocol on fixed version | Subset of A100 evaluation | Greenfield app: 1 iteration; Maintenance: 1 iteration; Determinism: 5/5 |
| Verify P0 fixes | convert.try_to_int("12.50"), convert.to_float("3.5"), malformed input handling | No crashes on bad input |
| Verify P1 fixes | // warning, test runner, environment.args error, hangman | All work as specified |
| Performance regression check | Canonical 10k workload | No regression from ADR-017 baseline (980ms) |
| Documentation review | All updated docs | No contradictions, no missing constraints |

---

## 4. What Should NOT Change

### 4.1 Language Surface

| Element | Why it must NOT change |
|---------|----------------------|
| No loops (ADR-001/002) | Loops would break determinism and AI-maintainability. The no-loops design is a feature, not a bug. |
| No nested functions (ADR-004) | Top-level functions enable clear dependency graphs and bottom-up ordering. |
| // as comment syntax | Changing // to integer division would break existing code. Warning is sufficient. |
| ! as logical NOT | 
ot keyword is not needed. Adding it would increase language surface for no benefit. |
| # as non-comment | # is not a comment in AILang. Adding it would increase surface. |
| Bottom-up ordering (ADR-004) | This is a design trade-off that enables AI-maintainability. Forward declarations are a future enhancement, not A101 scope. |

### 4.2 Architecture

| Element | Why it must NOT change |
|---------|----------------------|
| Tree-walking interpreter | Dispatch overhead is 24.2%, well below 50% threshold. No VM justified. |
| Trampoline (ADR-017) | Works as designed for scalar tail calls. List/map limitations are known constraints, not architecture defects. |
| Deterministic semantics | Non-negotiable. Byte-identical output is the core differentiator. |
| max_recursion = 2000 | This is a safety limit, not a feature. Changing it would risk CPython stack overflow. |

### 4.3 Scope Boundaries

| Element | Why it is out of scope for A101 |
|---------|-------------------------------|
| Forward declaration syntax | High effort, high risk. ADR-004 trade-off is acceptable. |
| Native map/filter/reduce | Would require stdlib redesign. Defer to Phase 3+. |
| JIT/bytecode compilation | No evidence justifies. Dispatch is 24.2%. |
| General-purpose features | Stay focused on AI-first business software. |
| Python syntax compatibility | AILang is its own language, not Python with different syntax. |

---

## 5. Next Release Gate

### 5.1 Recommended Primary Path

**A) A101 Targeted Hardening**

**Why:** The A100 evidence is clear and sufficient. The P0 blockers are well-defined (F-01, F-02, F-03, F-14). The fixes are scoped and low-risk. No additional evidence collection is needed for the P0 items. The architecture is vindicated — no escalation required.

**What must be true before implementation begins:**

1. Phase 0 reproduction tasks complete (confirm or reject F-04)
2. Project owner approves this hardening plan
3. ADRs created for each P0 fix (float parsing, safe parse)
4. No conflicting strategic direction from V2 reviewers

### 5.2 What Would Change This Path

| Event | New path |
|-------|----------|
| F-04 (cumulative budget) confirmed at <200 records | Escalate to architecture investigation |
| V2 reviewers demand VM before business-ready | Path C: architecture investigation |
| Additional evaluator uncovers new P0 | Re-evaluate after Phase 0 |
| Performance regression in Phase 5 | Gate A investigation |

---

## 6. Project Memory Update

### 6.1 A100 Completion Status

| Field | Value |
|-------|-------|
| **Status** | COMPLETE |
| **Evaluators** | 5 independent blind developers |
| **Confirmed findings** | 13 product issues, 8 documentation issues |
| **Rejected findings** | 1 (evaluator error) |
| **Design trade-offs** | 2 (accepted) |
| **Unconfirmed findings** | 1 (F-04 cumulative budget — requires reproduction) |
| **Architecture verdict** | CONTINUE — tree-walking interpreter + trampoline |
| **Next authorized gate** | A101 Targeted Hardening |

### 6.2 Evidence Gates Status

| Gate | Status | Evidence |
|------|--------|----------|
| A: Determinism | PASS | 5/5 evaluators, byte-identical |
| B: Performance | PASS | 24.2% dispatch overhead |
| C: 10k Workload | PARTIAL | Achievable for single-pass, not multi-pass |
| D: Business Ready | PARTIAL | Greenfield PASS, maintenance PASS, but P0 blockers remain |
| E: AI-Maintainable | PASS | Spec accuracy + change accuracy confirmed |
| F: Error Handling | FAIL | No try/catch, no safe parse |
| G: Money Safe | FAIL | No float parsing |

### 6.3 Priority for v1.1.22

1. P0: convert.try_to_int() + convert.try_to_float() + convert.to_float()
2. P0: Document recursion constraints + batching workaround
3. P0: Fix bundled hangman app
4. P1: // expression warning
5. P1: environment.args error message
6. P1: Incomplete statement parser fix
7. P1: Test runner improvements
8. P2/P3: Documentation fixes

---

*Plan generated: 2026-08-20*
*Status: PLANNING COMPLETE*
*Next action: Project owner review and approval*
*Authorization required before any code changes*
