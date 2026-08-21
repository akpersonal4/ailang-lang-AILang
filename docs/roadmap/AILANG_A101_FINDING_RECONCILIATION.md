# AILang A101 — Master Finding Reconciliation

> **Status:** ANALYSIS ONLY — No code, no fixes, no version changes
>
> **Source:** A100 Consolidated Report + all five blind evaluator reports + ADR-017 + V2 Strategic Plan
>
> **Date:** 2026-08-20

---

## 1. Purpose

This document provides a finding-by-finding reconciliation of every significant
observation from the A100 community validation. For each finding it records the
exact evidence, classification, severity, confidence, and recommended disposition.
It also reconciles every conflict between evaluators.

---

## 2. Master Finding Matrix

### 2.1 Language / Runtime Findings

#### F-01: No Float/Decimal String Parsing

| Field | Value |
|-------|-------|
| **ID** | F-01 |
| **Title** | No float/decimal string parsing |
| **Source evaluator(s)** | ALL (Dev1, Dev2, Dev3, Dev4, Dev5) |
| **Classification** | A — CONFIRMED PRODUCT ISSUE |
| **Severity** | P0 |
| **Reproduced by** | 5/5 evaluators |
| **Exact evidence** | `convert.to_int("12.50")` raises RuntimeError. `convert.to_number("3.5")` is alias for `to_int`, also raises. No `convert.to_float()` exists. Dev4 confirmed via source inspection: `builtins.py :: native_to_int -> int(value)` is the only path. |
| **Affected workload** | Any financial/business application reading currency from CSV, JSON, or user input |
| **User/business impact** | Every financial app must implement manual integer-cents parsing. Blocks V2 P0-3 money contract. |
| **Root cause type** | stdlib limitation (missing API) |
| **Workaround** | Integer-cents parsing via `string.split` + `convert.to_int` (Dev1, Dev4, Dev5 independently discovered same pattern) |
| **Frequency/likelihood** | 100% for any financial workload |
| **Correctness impact** | Cannot parse decimal strings at all — not a correctness bug, a missing capability |
| **Performance impact** | None (workaround adds ~5 lines of boilerplate) |
| **AI-maintenance impact** | Low — the workaround pattern is consistent and teachable |
| **Conflicts with other evaluator** | None — all 5 agree |
| **Confidence** | HIGH |
| **Recommended disposition** | FIX (add `convert.to_float()` + `convert.try_to_int()` / `convert.try_to_float()`) |

---

#### F-02: No Exception Handling / Safe Numeric Parse

| Field | Value |
|-------|-------|
| **ID** | F-02 |
| **Title** | No exception handling or safe numeric parse |
| **Source evaluator(s)** | Dev2, Dev4, Dev5 |
| **Classification** | A — CONFIRMED PRODUCT ISSUE |
| **Severity** | P0 |
| **Reproduced by** | 3/5 evaluators |
| **Exact evidence** | Dev4 file-write side-effect test: `test.expect` failure prevented subsequent file write — no intra-file recovery possible. Dev5: `bad_bad_price.csv` → crash at `convert.to_int`. Dev2: malformed numeric field terminates entire program. |
| **Affected workload** | Any application processing untrusted external input |
| **User/business impact** | Single malformed field crashes entire program. Batch jobs lose all progress on first bad value. |
| **Root cause type** | language-design limitation (no try/catch or Result type) |
| **Workaround** | None clean. Manual string validation before `convert.to_int` is fragile and incomplete. |
| **Frequency/likelihood** | 100% when processing real-world data with any malformation |
| **Correctness impact** | Complete program termination on single bad input |
| **Conflicts with other evaluator** | None |
| **Confidence** | HIGH |
| **Recommended disposition** | FIX (add `convert.try_to_int()` / `convert.try_to_float()` returning sentinel on failure) |

---

#### F-03: Recursion Constraints for List/Map Workloads

| Field | Value |
|-------|-------|
| **ID** | F-03 |
| **Title** | Recursion constraints for list/map-carrying workloads |
| **Source evaluator(s)** | Dev1, Dev2, Dev4, Dev5 |
| **Classification** | A — CONFIRMED PRODUCT ISSUE (workload-specific nuance) |
| **Severity** | P0 |
| **Reproduced by** | 4/5 evaluators |
| **Exact evidence** | Dev1: `build_list(5000, ...)` → "Recursion depth exceeded (limit: 2000)". Dev5: 5k works, 10k fails at 2000 limit. ADR-017 Phase 2: scalar tail recursion works to 20k. Dev2: multi-pass apps exhaust cumulative 100k budget at ~500-600 records. |
| **Affected workload** | Any workload recursing over lists/maps with >2000 elements |
| **User/business impact** | Canonical 10k business workload achievable only for single-pass scalar patterns |
| **Root cause type** | language-design limitation (trampoline handles scalar tail calls; list/map calls fall back to host stack) |
| **Workaround** | Batching recursion (Dev1: 500-row batches → 10k at 1,589ms). Not documented. |
| **Conflicts with other evaluator** | See reconciliation section 3.1 |
| **Confidence** | HIGH (2k depth limit: 4 evaluators; 100k budget: 1 evaluator, requires reproduction) |
| **Recommended disposition** | DOCUMENT (limits + workaround) + INVESTIGATE (trampoline extension for list/map tail calls) |

---

#### F-04: Cumulative Recursion Budget (100k Shared Counter)

| Field | Value |
|-------|-------|
| **ID** | F-04 |
| **Title** | Cumulative 100,000-iteration budget shared across program |
| **Source evaluator(s)** | Dev2 only |
| **Classification** | B — WORKLOAD-SPECIFIC ISSUE |
| **Severity** | P1 |
| **Reproduced by** | 1/5 evaluators |
| **Exact evidence** | Dev2: `_trampoline_iterations` counter (limit: `max_call_depth * 50 = 100,000`) incremented by both top-level trampoline AND nested `_inline_tail_chain`. Resets only at fresh top-level `_trampoline_call`. Multi-pass apps exhaust at ~500-600 records. |
| **Affected workload** | Multi-pass applications chaining recursive helpers within one `main()` |
| **Conflicts with other evaluator** | See reconciliation section 3.2 |
| **Confidence** | MEDIUM (single evaluator, requires controlled reproduction) |
| **Recommended disposition** | RE-TEST (controlled reproduction required) |

---

#### F-05: Silent `//` Comment Trap

| Field | Value |
|-------|-------|
| **ID** | F-05 |
| **Title** | `//` is line comment, not integer division — silent wrong answer |
| **Source evaluator(s)** | Dev4, Dev5 |
| **Classification** | A — CONFIRMED PRODUCT ISSUE |
| **Severity** | P1 |
| **Reproduced by** | 2/5 evaluators |
| **Exact evidence** | Dev4: `10 // 3 = 10` (`// 3` treated as comment). Dev5: confirmed identically. |
| **Affected workload** | Any Python/C/Java/JS developer; any AI model generating code |
| **User/business impact** | Silent logic corruption — no error, no warning |
| **Root cause type** | language-design trade-off + documentation gap |
| **Confidence** | HIGH |
| **Recommended disposition** | FIX (emit warning when `//` in expression context) + DOCUMENT |

---

#### F-06: Test Runner Granularity and Abort Behavior

| Field | Value |
|-------|-------|
| **ID** | F-06 |
| **Title** | `ail test` counts files not functions; aborts on first failure per file |
| **Source evaluator(s)** | Dev1, Dev2, Dev4, Dev5 |
| **Classification** | A — CONFIRMED PRODUCT ISSUE |
| **Severity** | P1 |
| **Reproduced by** | 4/5 evaluators |
| **Exact evidence** | Dev4 file-write side-effect test: file after failing `test.expect` never created. Dev1: "1/1 passed" counts files. Dev2, Dev5: same. |
| **Confidence** | HIGH |
| **Recommended disposition** | FIX (per-function reporting + `--continue-on-fail`) |

---

#### F-07: `environment.args` Internal Compiler Error

| Field | Value |
|-------|-------|
| **ID** | F-07 |
| **Title** | `environment.args` without parens triggers CMP001 internal error |
| **Source evaluator(s)** | Dev1 |
| **Classification** | A — CONFIRMED PRODUCT ISSUE |
| **Severity** | P2 |
| **Reproduced by** | 1/5 evaluators |
| **Confidence** | HIGH |
| **Recommended disposition** | FIX (add "did you mean" diagnostic) |

---

#### F-08: Incomplete Statement Silently Ignored

| Field | Value |
|-------|-------|
| **ID** | F-08 |
| **Title** | `let x =` (incomplete assignment) silently ignored |
| **Source evaluator(s)** | Dev1 |
| **Classification** | A — CONFIRMED PRODUCT ISSUE |
| **Severity** | P2 |
| **Reproduced by** | 1/5 evaluators |
| **Confidence** | HIGH |
| **Recommended disposition** | FIX (parser should error on incomplete `let`) |

---

#### F-09: Bundled Hangman App Crashes Interpreter

| Field | Value |
|-------|-------|
| **ID** | F-09 |
| **Title** | Bundled hangman_game crashes interpreter silently |
| **Source evaluator(s)** | Dev1 |
| **Classification** | A — CONFIRMED PRODUCT ISSUE |
| **Severity** | P1 |
| **Reproduced by** | 1/5 evaluators |
| **Exact evidence** | Dev1: ~2/17 runs crash with exit -1, no error. Root cause: re-picking guessed letters → unbounded recursion. Fix: filter alphabet (10/10 pass after). |
| **Confidence** | HIGH |
| **Recommended disposition** | FIX (fix app or remove from wheel) |

---

#### F-10: Recursion Pass-by-Value Silent Bugs

| Field | Value |
|-------|-------|
| **ID** | F-10 |
| **Title** | Recursion with pass-by-value accumulators produces silent wrong results |
| **Source evaluator(s)** | Dev4, Dev5 |
| **Classification** | A — CONFIRMED PRODUCT ISSUE |
| **Severity** | P2 |
| **Reproduced by** | 2/5 evaluators |
| **Confidence** | HIGH |
| **Recommended disposition** | DOCUMENT (accumulator patterns guidance) |

---

#### F-11: Runtime Errors in Imported Modules Misattributed

| Field | Value |
|-------|-------|
| **ID** | F-11 |
| **Title** | Errors in imported modules reported at wrong source location |
| **Source evaluator(s)** | Dev2 |
| **Classification** | B — WORKLOAD-SPECIFIC ISSUE |
| **Severity** | P2 |
| **Reproduced by** | 1/5 evaluators |
| **Confidence** | MEDIUM |
| **Recommended disposition** | DEFER |

---

#### F-12: `string.split` Does Not Split on Newlines

| Field | Value |
|-------|-------|
| **ID** | F-12 |
| **Title** | `string.split(text, " ")` does not treat newlines as whitespace |
| **Source evaluator(s)** | Dev2 |
| **Classification** | B — WORKLOAD-SPECIFIC ISSUE |
| **Severity** | P2 |
| **Reproduced by** | 1/5 evaluators |
| **Confidence** | MEDIUM |
| **Recommended disposition** | DOCUMENT or FIX (add `string.split_lines()`) |

---

#### F-13: `static_analyzer` Ships with Stubs

| Field | Value |
|-------|-------|
| **ID** | F-13 |
| **Title** | `static_analyzer` stdlib module has stub functions |
| **Source evaluator(s)** | Dev2 |
| **Classification** | A — CONFIRMED PRODUCT ISSUE |
| **Severity** | P2 |
| **Reproduced by** | 1/5 evaluators |
| **Confidence** | HIGH |
| **Recommended disposition** | DOCUMENT (mark incomplete) or REMOVE |

---

### 2.2 Documentation Findings

#### F-14: Recursion Limit Not Documented

| Field | Value |
|-------|-------|
| **ID** | F-14 |
| **Title** | 2000 recursion limit not in GETTING_STARTED or LANGUAGE_SPEC |
| **Source evaluator(s)** | Dev1, Dev2, Dev5 |
| **Classification** | E — DOCUMENTATION ISSUE |
| **Severity** | P1 |
| **Reproduced by** | 3/5 evaluators |
| **Confidence** | HIGH |
| **Recommended disposition** | DOCUMENT |

#### F-15: UTF-8 BOM Rejection Undocumented

| Field | Value |
|-------|-------|
| **ID** | F-15 |
| **Title** | BOM character rejected with LEX001; Windows editors emit BOM |
| **Source evaluator(s)** | Dev4, Dev5 |
| **Classification** | E — DOCUMENTATION ISSUE |
| **Severity** | P3 |
| **Reproduced by** | 2/5 evaluators |
| **Confidence** | HIGH |
| **Recommended disposition** | DOCUMENT |

#### F-16: `convert.to_number` Name Misleading

| Field | Value |
|-------|-------|
| **ID** | F-16 |
| **Title** | `convert.to_number` implies float support, is alias for `to_int` |
| **Source evaluator(s)** | Dev1, Dev2, Dev3, Dev5 |
| **Classification** | E — DOCUMENTATION ISSUE |
| **Severity** | P2 |
| **Reproduced by** | 4/5 evaluators |
| **Confidence** | HIGH |
| **Recommended disposition** | DOCUMENT |

#### F-17: `list.sort` Documentation Contradiction

| Field | Value |
|-------|-------|
| **ID** | F-17 |
| **Title** | STDLIB_REFERENCE main section implies in-place sort; gotchas says returns new list |
| **Source evaluator(s)** | Dev2 |
| **Classification** | E — DOCUMENTATION ISSUE |
| **Severity** | P2 |
| **Reproduced by** | 1/5 evaluators |
| **Confidence** | HIGH |
| **Recommended disposition** | DOCUMENT |

#### F-18: `environment.args` Doc Entry Missing Function-Call Signal

| Field | Value |
|-------|-------|
| **ID** | F-18 |
| **Title** | `environment.args` documented without signaling it requires parentheses |
| **Source evaluator(s)** | Dev1 |
| **Classification** | E — DOCUMENTATION ISSUE |
| **Severity** | P2 |
| **Reproduced by** | 1/5 evaluators |
| **Confidence** | HIGH |
| **Recommended disposition** | DOCUMENT |

#### F-19: `SEM001` Wording Overstates Restriction

| Field | Value |
|-------|-------|
| **ID** | F-19 |
| **Title** | `SEM001` fires even when inner block reuse is allowed |
| **Source evaluator(s)** | Dev4, Dev5 |
| **Classification** | E — DOCUMENTATION ISSUE |
| **Severity** | P3 |
| **Reproduced by** | 2/5 evaluators |
| **Confidence** | HIGH |
| **Recommended disposition** | DOCUMENT |

#### F-20: `string.substring` Semantics Unclear

| Field | Value |
|-------|-------|
| **ID** | F-20 |
| **Title** | `string.substring(str, start, end)` behavior not clearly documented |
| **Source evaluator(s)** | Dev4 |
| **Classification** | E — DOCUMENTATION ISSUE |
| **Severity** | P3 |
| **Reproduced by** | 1/5 evaluators |
| **Confidence** | MEDIUM |
| **Recommended disposition** | DOCUMENT |

#### F-21: Semicolons Documented as Required but Optional

| Field | Value |
|-------|-------|
| **ID** | F-21 |
| **Title** | LANGUAGE_SPEC says semicolons required; they are actually optional |
| **Source evaluator(s)** | Dev2 |
| **Classification** | E — DOCUMENTATION ISSUE |
| **Severity** | P3 |
| **Reproduced by** | 1/5 evaluators |
| **Confidence** | HIGH |
| **Recommended disposition** | DOCUMENT |

---

### 2.3 Evaluator / Application Errors

#### F-22: `sum_transactions()` Returns Wrong Total (Dev3)

| Field | Value |
|-------|-------|
| **ID** | F-22 |
| **Title** | Dev3's `sum_transactions` returns first record only |
| **Source evaluator(s)** | Dev3 only |
| **Classification** | D — APPLICATION/EVALUATOR ERROR |
| **Severity** | N/A |
| **Confidence** | HIGH (evaluator error, not language defect) |
| **Recommended disposition** | REJECT |

#### F-23: `#` Comments, `not` Keyword, Nested Functions (Dev3)

| Field | Value |
|-------|-------|
| **ID** | F-23 |
| **Title** | Dev3 found friction with `#` comments, `not` keyword, nested functions |
| **Source evaluator(s)** | Dev3 |
| **Classification** | F — ENHANCEMENT (language design choices) |
| **Severity** | P3 |
| **Confidence** | HIGH (documented behavior) |
| **Recommended disposition** | ACCEPT (design trade-off) |

#### F-24: Bottom-Up Ordering Friction

| Field | Value |
|-------|-------|
| **ID** | F-24 |
| **Title** | Bottom-up function ordering creates friction for developers |
| **Source evaluator(s)** | Dev1, Dev3, Dev4, Dev5 |
| **Classification** | F — ENHANCEMENT (language design choice per ADR-004) |
| **Severity** | P2 |
| **Reproduced by** | 4/5 evaluators |
| **Confidence** | HIGH |
| **Recommended disposition** | ACCEPT (forward declarations are future enhancement, not A101 scope) |

---

## 3. Conflict Reconciliation

### 3.1 Recursion / 10k Behavior

| Evaluator | Observation |
|-----------|-------------|
| Dev1 | 10k works with batching. Scalar tail recursion works to 10k. List/map fails at 2000. |
| Dev2 | 10k unreachable for multi-pass. Cumulative 100k budget exhausted at ~500-600 records. |
| Dev3 | Did not test beyond 1000. No limit observed. |
| Dev4 | 10k completes in 13.5s (single-pass aggregation). |
| Dev5 | 5k works. 10k fails at 2000 limit. |

**Can all be true?** YES. Fully explained by workload differences:
- Dev1 used batching → avoids both limits. Works.
- Dev2 used multi-pass recursion → exhausts cumulative budget. Fails at ~500-600.
- Dev4 used single-pass aggregation → stays within limits. Works at 10k but slow.
- Dev5 used per-product per-sale map aggregation → hits 2000 depth at 10k. Fails.

**Is it a product defect?** YES — the constraints are real. Severity depends on workload pattern.

**Another measurement required?** YES — for F-04 (cumulative budget). The 2000 depth limit is established.

### 3.2 Cumulative Recursion Budget

| Evaluator | Observation |
|-----------|-------------|
| Dev2 | Multi-pass apps exhaust at ~500-600 records. Fully tail-recursive rewrite fails at same threshold. `_trampoline_iterations` counter shared across program. |
| All others | Did not test multi-pass patterns at scale. Dev4's single-pass app completed 10k. |

**Can both be true?** YES. Dev2's multi-pass pattern charges the cumulative budget multiple times per record (once per pass). Dev4's single-pass pattern charges it once per record. The difference is the number of recursive passes per record, not a contradiction.

**Is it a product defect?** It is a design constraint (cumulative budget is intentional to prevent runaway). But the budget may be too low for realistic multi-pass workloads. Requires controlled reproduction.

### 3.3 Malformed CSV Handling

| Evaluator | Observation |
|-----------|-------------|
| Dev1 | `csv.parse_header` silently returns row with empty/missing values |
| Dev2 | Unclosed quote accepted silently, exit 0 |
| Dev3 | "Handled gracefully (2 of 3 rows processed)" |

**Can all be true?** YES — different malformation types:
- Dev1: missing fields → parsed with empty values (silent)
- Dev2: unclosed quote → accepted silently (no validation)
- Dev3: inconsistent field count → partially processed

**Is it a product defect?** It is a design choice: `csv.parse` does not validate structure. It parses what it can. Should be documented.

### 3.4 Performance Ratios

| Evaluator | Ratio | Workload |
|-----------|-------|----------|
| Dev1 | ~92x | Expense batched 10k |
| Dev2 | ~3-4x | CSV/word tasks |
| Dev4 | ~887x (N=100) to ~288x (N=10k) | Expense aggregation |
| Dev5 | ~10x (N=100) to ~115x (N=5k) | Inventory map-based |

**Can all be true?** YES. Ratios differ because:
- Dev2: lighter workload (CSV parsing is native) → lower ratio
- Dev4: includes compile overhead (dominates at N=100: 514ms/603ms = 85%) → inflated at small N
- Dev5: map-based single-pass → different recursion pattern than Dev4

**Key insight:** The ratio is NOT a single number. It depends on workload type, N, and whether compile is included.

---

## 4. Priority Classification

### P0 — Release/Business Blockers

| ID | Finding | Justification |
|----|---------|---------------|
| F-01 | No float/decimal string parsing | Blocks V2 P0-3 money contract. 5/5 confirm. |
| F-02 | No exception handling / safe parse | Blocks safe untrusted input processing. 3/5 confirm. |
| F-03 | Recursion constraints for list/map workloads | Blocks 10k for realistic patterns. 4/5 confirm. |
| F-14 | Recursion limit not documented | Developers hit 2000 cold. 3/5 confirm. |

### P1 — Must Fix Before Claiming Business-Ready

| ID | Finding | Justification |
|----|---------|---------------|
| F-04 | Cumulative recursion budget | If confirmed, blocks multi-pass at ~500. Requires reproduction. |
| F-05 | Silent `//` comment trap | Silent wrong answers. 2/5 confirm. |
| F-06 | Test runner granularity | First failure hides all others. 4/5 confirm. |
| F-09 | Bundled hangman crashes | Shipped app crashes interpreter. 1/5 confirm. |
| F-10 | Pass-by-value silent bugs | Silent wrong answers. 2/5 confirm. |

### P2 — Important Engineering Improvement

| ID | Finding | Justification |
|----|---------|---------------|
| F-07 | `environment.args` internal error | 1/5. |
| F-08 | Incomplete statement silently ignored | 1/5. |
| F-11 | Error misattribution in modules | 1/5. |
| F-12 | `string.split` newline behavior | 1/5. |
| F-13 | `static_analyzer` stubs | 1/5. |
| F-16 | `convert.to_number` name misleading | 4/5. |
| F-17 | `list.sort` docs contradictory | 1/5. |
| F-18 | `environment.args` doc entry | 1/5. |
| F-24 | Bottom-up ordering friction | 4/5 (design trade-off). |

### P3 — Documentation/Usability

| ID | Finding | Justification |
|----|---------|---------------|
| F-15 | UTF-8 BOM rejection undocumented | 2/5. |
| F-19 | `SEM001` wording too broad | 2/5. |
| F-20 | `string.substring` docs unclear | 1/5. |
| F-21 | Semicolons optional not documented | 1/5. |
| F-23 | `#`/`not`/nested functions friction | 1/5 (design choices). |

### Summary Counts

| Category | Count |
|----------|-------|
| CONFIRMED PRODUCT ISSUE | 13 |
| WORKLOAD-SPECIFIC | 4 |
| DOCUMENTATION | 8 |
| EVALUATOR ERROR | 1 |
| DESIGN TRADE-OFF | 2 |
| **Total findings** | **24** |

| Priority | Count |
|----------|-------|
| P0 | 4 |
| P1 | 5 |
| P2 | 9 |
| P3 | 5 |
| P4 | 1 |
| **Total** | **24** |
