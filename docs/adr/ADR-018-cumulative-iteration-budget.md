# ADR-018: F-04 — Cumulative Iteration Budget

**Date:** 2026-08-20
**Status:** APPROVED (2026-08-21) — acceptance review verdict APPROVED; all 4 review conditions incorporated and verified in `AILANG_A101_ADR018_ACCEPTANCE_REVIEW.md`
**Supersedes:** nothing
**Superseded by:** nothing
**Related ADRs:** ADR-017 (trampoline execution model), ADR-001 (recursion-only iteration)
**Finding:** F-04 (cumulative 100,000-iteration budget shared across program)
**Strategic Plan:** `AILANG_STRATEGIC_ENGINEERING_PLAN_V2.md`

---

## 1. Context

AILang uses a trampoline (ADR-017 Option E) to execute tail-recursive calls without growing the Python host stack. The trampoline enforces a safety limit of `max_call_depth * 50 = 100,000` iterations to prevent infinite recursion from consuming unbounded memory.

Phase 0 reproduction confirmed that this limit is **cumulative across the entire program execution** rather than per-chain. When multiple independent recursive workloads execute sequentially within a single `main()`, they share the same 100,000-iteration budget. A workload that consumes 50,000 iterations leaves only 50,000 for subsequent workloads, causing the second to fail even though its own depth is well within the limit.

This means a multi-pass business pipeline (build → filter → sum) with >500 records per pass can exhaust the cumulative budget and crash, even though each individual pass is well within the 100,000 limit.

---

## 2. Confirmed F-04 Evidence

| Test | Workload | Result |
|------|----------|--------|
| `deep_scalar(50000, 0)` solo | 50k scalar tail recursion | **PASS** |
| `deep_list(60000, items)` solo | 60k list-carrying recursion | **PASS** |
| `deep_scalar(95000, 0)` solo | 95k scalar tail recursion | **PASS** |
| `deep_scalar(50000)` then `deep_list(60000)` | Sequential workloads | **FAIL** at 110k cumulative |
| 400-record build/validate/sum pipeline | Multi-pass business workload | **PASS** (~1200 iterations) |

**Root cause:** `_inline_tail_chain` (interpreter.py:534) increments `_trampoline_iterations` without saving/restoring it. The counter is shared with the enclosing `_trampoline_call` loop, causing sequential function calls within one trampoline invocation to accumulate iterations against a single budget.

**Key implementation trace:**

| Component | Iteration counter behavior | Location |
|-----------|---------------------------|----------|
| `_trampoline_call` | Saves/restores `_trampoline_iterations` (lines 451, 516). Resets to 0 on entry (line 458). Each invocation gets a fresh budget. | interpreter.py:431–518 |
| `_inline_tail_chain` | Does NOT save/restore `_trampoline_iterations`. Increments the same counter (line 534) as the enclosing `_trampoline_call`. | interpreter.py:520–572 |
| `_call_function` | Enforces `_call_depth > _max_call_depth` (2000 limit) for non-trampoline calls. Does NOT check `_trampoline_iterations`. | interpreter.py:349–413 |
| `execute` | Entry point. Calls `_trampoline_call` for main (line 155). | interpreter.py:149–197 |
| `call_function` | Public entry for `ail test`. Also calls `_trampoline_call` (line 826). | interpreter.py:799–826 |

**Execution flow for sequential workloads:**

```
main() → _trampoline_call(main, ())
  iterations = 0  (reset on entry)
  ↓ trampoline loop pops main
  ↓ _call_function(main) → _execute_block(main.body)
    ↓ deep_scalar(50000) → _call_function → _inline_tail_chain
      iterations += 50000  (shared counter)
      returns; iterations stays at 50000
    ↓ deep_list(60000) → _call_function → _inline_tail_chain
      iterations += 60000  (same counter)
      total = 110000 > 100000 → ERROR
  ↓ finally: iterations restored to saved value (0)
```

---

## 3. Problem Statement

The trampoline iteration budget is cumulative within a single `_trampoline_call` invocation. Independent recursive workloads (sequential function calls from `main()`) share the same 100,000-iteration budget. This causes:

1. **False failures** on legitimate multi-pass business pipelines with >500 records per pass
2. **Misleading error messages** — "limit: 2000" when the actual constraint is 100,000 cumulative iterations
3. **Fragile workload sizing** — developers must mentally track cumulative iteration consumption across all functions in `main()`

---

## 4. Design Invariants

| # | Invariant | Justification |
|---|-----------|---------------|
| I-1 | Infinite recursion must remain bounded | Safety — prevents unbounded memory consumption |
| I-2 | Mutual recursion must remain bounded | Safety — prevents cross-function infinite loops |
| I-3 | Tail recursion must remain deterministic | ADR-017 acceptance criterion F-2 |
| I-4 | 10k canonical workload must pass | V2 §5B product target |
| I-5 | Existing valid programs must retain behavior | Backward compatibility — ADR-017 §7.5 |
| I-6 | No grammar/AST/IR/stdlib/API changes unless proven necessary | Minimal change principle |
| I-7 | Error message must identify the correct limit and limit type | F-14 documented issue |
| I-8 | `max_recursion` and iteration budget remain separate concepts | `max_recursion` = host stack safety; iteration budget = trampoline runaway protection |

---

## 5. Options Evaluated

### Option A: Keep one global program-wide budget (status quo)

**Semantics:** All recursive workloads within a program share a single 100,000-iteration budget. The budget is never reset.

| Axis | Assessment |
|------|-----------|
| Correctness | Correct — catches all forms of runaway recursion |
| 10k business workload | **FAIL** — multi-pass pipelines with >500 records exhaust cumulative budget |
| Nested function behavior | Correct — nested calls share budget (intended) |
| Tail-call/trampoline semantics | Correct — trampoline loop enforces limit |
| Non-tail recursion | Correct — `_call_depth` enforces 2000 limit independently |
| Determinism | Preserved — same iterations produce same result |
| Memory safety | Preserved — budget prevents unbounded memory |
| Infinite recursion protection | Strong — any infinite chain hits 100k limit |
| Performance overhead | Zero — no additional state |
| Error reporting | **MISLEADING** — says "limit: 2000" when actual limit is 100,000 |
| AI-maintainability | Poor — developers must mentally track cumulative consumption |
| Backward compatibility | Perfect — no observable change |
| Testability | High — simple single-counter model |
| Implementation complexity | None (status quo) |
| Interaction with max_recursion | Independent — `max_recursion` enforces host stack depth |
| Interaction with ADR-017 | Compatible — trampoline works as designed |
| 10k business-record requirement | **FAIL** — cumulative budget blocks multi-pass at ~500 records |

**Verdict: REJECT** — fails I-4 (10k workload) and I-7 (error reporting).

---

### Option B: Reset the budget for each top-level execution/workload

**Semantics:** Reset `_trampoline_iterations` to 0 before each top-level function call from `main()`.

| Axis | Assessment |
|------|-----------|
| Correctness | Correct for independent workloads |
| 10k business workload | **PASS** — each workload gets fresh 100k budget |
| Nested function behavior | Correct — nested calls within a workload share budget |
| Tail-call/trampoline semantics | Correct — trampoline loop enforces limit per workload |
| Non-tail recursion | Correct — `_call_depth` enforces 2000 limit independently |
| Determinism | Preserved |
| Memory safety | Preserved — each workload bounded at 100k |
| Infinite recursion protection | **WEAKENED** — mutual recursion across workloads could exceed 100k total |
| Performance overhead | Zero |
| Error reporting | Improved — each workload has clear budget |
| AI-maintainability | Good — each function call is independent |
| Backward compatibility | **RISK** — changes observable behavior for programs that depend on cumulative budget |
| Testability | High |
| Implementation complexity | Low — add reset in `_execute_block` before each call from main |
| Interaction with max_recursion | Independent |
| Interaction with ADR-017 | Compatible |
| 10k business-record requirement | **PASS** |

**Problem:** "Top-level workload" is ill-defined. `main()` is the only true top-level entry. Sequential calls within `main()` are not independent — they share state (variables, lists). Resetting between calls would mean `build_list(10000)` uses 50k iterations, then `filter_list(...)` gets a fresh 100k, then `sum_list(...)` gets another fresh 100k. Total = 250k iterations, but each is bounded. However, mutual recursion across workloads (e.g., `f` calls `g` calls `f`) would not be caught if each call resets.

**Verdict: REJECT** — "top-level workload" is not a well-defined concept in AILang's execution model. The boundary is ambiguous.

---

### Option C: Per-call-chain budget

**Semantics:** Each call to `_inline_tail_chain` saves and restores `_trampoline_iterations`, giving each chain an independent 100,000-iteration budget.

| Axis | Assessment |
|------|-----------|
| Correctness | Correct — each chain is independently bounded |
| 10k business workload | **PASS** — each function call gets its own 100k budget |
| Nested function behavior | Correct — nested calls create new chains with own budgets |
| Tail-call/trampoline semantics | Correct — trampoline loop processes one chain at a time |
| Non-tail recursion | Correct — `_call_depth` enforces 2000 limit independently |
| Determinism | Preserved |
| Memory safety | Preserved — each chain bounded at 100k |
| Infinite recursion protection | Correct — any infinite chain hits 100k limit |
| Performance overhead | Minimal — save/restore of one integer per chain entry |
| Error reporting | Clear — error identifies which chain exceeded limit |
| AI-maintainability | Good — each function call is independently bounded |
| Backward compatibility | **IMPROVED** — programs that previously failed at ~500 records now succeed |
| Testability | High — each chain is testable independently |
| Implementation complexity | Low — add save/restore in `_inline_tail_chain` (4 lines) |
| Interaction with max_recursion | Independent — `max_recursion` enforces host stack depth |
| Interaction with ADR-017 | Compatible — trampoline loop unchanged |
| 10k business-record requirement | **PASS** |

**Key insight:** The trampoline loop's own `_trampoline_iterations` check (line 474) becomes less relevant with per-chain isolation, because `_inline_tail_chain` runs to completion before the trampoline loop processes the next item. The trampoline loop's check only fires for items pushed directly onto `_trampoline_stack` (depth==1 tail calls), not for items handled by `_inline_tail_chain` (depth>1 tail calls).

**Verdict: RECOMMEND** — simplest correct solution, satisfies all invariants.

---

### Option D: Hybrid safety model (per-chain + global runaway protection)

**Semantics:** Per-chain budget (Option C) plus a separate global iteration counter that accumulates across all chains.

| Axis | Assessment |
|------|-----------|
| Correctness | Correct — two layers of protection |
| 10k business workload | **PASS** — per-chain budget allows independent workloads |
| Nested function behavior | Correct |
| Tail-call/trampoline semantics | Correct |
| Non-tail recursion | Correct |
| Determinism | Preserved |
| Memory safety | Preserved — global counter prevents total runaway |
| Infinite recursion protection | Strongest — per-chain + global |
| Performance overhead | Low — two counters instead of one |
| Error reporting | Complex — two possible error sources |
| AI-maintainability | Medium — two limits to explain |
| Backward compatibility | Same as Option C |
| Testability | Medium — need to test both limits |
| Implementation complexity | Medium — two counters, two checks, two error messages |
| Interaction with max_recursion | Independent |
| Interaction with ADR-017 | Compatible |
| 10k business-record requirement | **PASS** |

**Trade-off:** Option D provides marginally stronger safety (global runaway protection) at the cost of increased complexity. The question is whether the additional safety justifies the complexity.

**Analysis:** The trampoline loop already serves as a de facto global safety net. It processes one item per `_trampoline_call` invocation. Even with per-chain isolation, the trampoline loop's own `_trampoline_iterations` check (line 474) still fires if the loop itself spins too many times (e.g., a function that pushes many items onto `_trampoline_stack`). This existing check provides adequate global runaway protection.

**Verdict: ACCEPTABLE but unnecessary** — the trampoline loop's existing check provides sufficient global protection. Option C is simpler and equally safe for all realistic workloads.

---

### Option E: Another design

**Semantics:** Would require evidence that Options A–D are insufficient.

**Analysis:** Option C satisfies all 17 evaluation axes. No evidence demonstrates insufficiency.

**Verdict: NOT REQUIRED** — Option C is sufficient.

---

## 6. Decision Matrix

| Axis | Weight | A: global | B: reset | C: per-chain | D: hybrid |
|------|--------|-----------|----------|-------------|-----------|
| Correctness | HIGH | ✓ | ✓ | ✓ | ✓ |
| 10k workload | HIGH | ✗ | ✓ | ✓ | ✓ |
| Infinite recursion | HIGH | ✓ | △ | ✓ | ✓ |
| Mutual recursion | HIGH | ✓ | ✗ | ✓ | ✓ |
| Determinism | HIGH | ✓ | ✓ | ✓ | ✓ |
| Memory safety | HIGH | ✓ | ✓ | ✓ | ✓ |
| Error reporting | MED | ✗ | ✓ | ✓ | △ |
| AI-maintainability | MED | ✗ | ✓ | ✓ | △ |
| Backward compat | MED | ✓ | ✗ | ✓ | ✓ |
| Complexity | MED | ✓ | ✓ | ✓ | △ |
| Testability | MED | ✓ | ✓ | ✓ | △ |
| **Score** | | **8/12** | **9/12** | **12/12** | **10/12** |

---

## 7. Recommended Option

**Option C: Per-call-chain budget.**

Each call to `_inline_tail_chain` saves `_trampoline_iterations`, resets it to 0, runs its loop, then restores the saved value. This gives each call chain an independent 100,000-iteration budget while preserving the trampoline loop's existing safety mechanism as a global backstop.

---

## 8. Exact Semantics

### 8.1 What constitutes a "chain"

A **chain** is a sequence of tail-recursive calls drained by a single invocation of `_inline_tail_chain`. It begins when `_call_function` receives a `_TailCallSentinel` result and calls `_inline_tail_chain(function, args)`. It ends when `_inline_tail_chain` returns a non-sentinel result.

### 8.2 When the counter starts

Each chain's counter starts at 0 when `_inline_tail_chain` is entered.

### 8.3 When it resets

The counter resets to 0 at the start of each `_inline_tail_chain` invocation (after saving the previous value).

### 8.4 What happens across function calls

Sequential function calls from `main()` (e.g., `build_list(10000)` then `filter_list(...)`) each create their own chain via `_call_function` → `_TailCallSentinel` → `_inline_tail_chain`. Each chain gets an independent 100,000-iteration budget.

### 8.5 What happens across sequential top-level workloads

Same as 8.4 — each workload is a separate function call, each with its own chain and budget.

### 8.6 What happens with mutual recursion

Mutual recursion (e.g., `f` calls `g` calls `f`) where the calls are tail calls at depth>1 creates a single chain drained by `_inline_tail_chain`. The chain shares one 100,000-iteration budget. If the mutual recursion is infinite, it hits the limit.

If mutual recursion involves calls at depth==1 (pushed to `_trampoline_stack`), the trampoline loop processes them. Each trampoline loop iteration increments `_trampoline_iterations` (line 473). The trampoline loop's own check (line 474) enforces the limit.

### 8.7 What happens with tail recursion

Tail recursion at depth==1: pushed to `_trampoline_stack`, processed by trampoline loop. Counter incremented per loop iteration. Limit enforced at line 474.

Tail recursion at depth>1 with safe args: returned as `_TailCallSentinel`, drained by `_inline_tail_chain`. Counter starts fresh per chain.

### 8.8 What happens with nested tail calls

Nested tail calls (e.g., `main` calls `f`, `f` tail-calls `g`, `g` tail-calls `h`) at depth>1: each function call within the chain shares the chain's budget. The chain's counter increments per iteration.

### 8.9 What happens when the limit is exceeded

`_inline_tail_chain` raises `RuntimeError` with:
- Operation: `"call"`
- Reason: `"Recursion depth exceeded (limit: 100000). AILang recursion is bounded to prevent stack overflow."`
- Suggestion: `"Simplify recursive logic. The recursion limit is 100000 iterations per call chain; for larger iterations use multiple smaller batches."`

### 8.10 Exact error semantics

The error message must reference the **actual limit** (100,000 iterations per chain), not the `_max_call_depth` value (2000). The `_max_call_depth` value is the Python host stack limit, which is a separate concept enforced by `_call_function` at line 357.

### 8.11 Whether max_recursion and iteration_budget remain separate concepts

Yes. They are independent safety mechanisms:
- `max_recursion` (2000): Limits Python host stack depth. Enforced by `_call_function` at line 357. Prevents CPython stack overflow.
- `iteration_budget` (100,000): Limits trampoline iterations per chain. Enforced by `_inline_tail_chain` at lines 534–535 (increment + check) and `_trampoline_call` at line 474. Prevents infinite recursion from consuming unbounded memory.

---

## 9. Safety Model

### 9.1 Infinite recursion (single function)

A function that tail-calls itself infinitely (e.g., `f(n) { return f(n-1) }`) creates a single chain. The chain's counter increments per iteration. At 100,001 iterations, `_inline_tail_chain` raises `RuntimeError`. **Caught.**

### 9.2 Mutual recursion (two functions)

`f` tail-calls `g`, `g` tail-calls `f`. At depth>1, this is a single chain drained by `_inline_tail_chain`. Counter increments per iteration. At 100,001 iterations, `RuntimeError`. **Caught.**

At depth==1, the trampoline loop processes them. Each iteration increments `_trampoline_iterations`. At 100,001 iterations, the trampoline loop's check (line 474) fires. **Caught.**

### 9.3 Pathological multi-chain case

A function called 1001 times from `main()`, each call using 100 iterations via `_inline_tail_chain`. Total = 100,100 iterations across chains. Each chain is within its 100k budget. The trampoline loop processes 1001 items (one per `_TailCallSentinel`). The trampoline loop's counter increments once per item: 1001 iterations — well within the 100k limit. **Correctly allowed.** Each call is legitimate; the total is bounded by the trampoline loop's own limit.

### 9.4 Memory impact

Each chain's budget is 100,000 iterations. At ~1.2 KB per frame (ADR-017 §19.3), a chain at full budget uses ~120 MB. With per-chain isolation, multiple chains could theoretically consume more total memory than the cumulative model. However:
- The trampoline loop's own limit (100k iterations) bounds the total number of chains
- Realistic workloads use far fewer than 100k iterations per chain
- The 10k canonical workload uses ~10k iterations total

**Assessment: acceptable.** The memory impact is bounded by the trampoline loop's limit.

---

## 10. Error Model

### 10.1 Error message (per-chain budget exceeded)

```
Operation: call
Reason: Recursion depth exceeded (limit: 100000). AILang recursion is bounded to prevent stack overflow.
Suggestion: Simplify recursive logic. The recursion limit is 100000 iterations per call chain; for larger iterations use multiple smaller batches.
Location: <source location of the recursive call>
```

### 10.2 Error message (host stack depth exceeded)

```
Operation: call
Reason: Recursion depth exceeded (limit: 2000). AILang recursion is bounded to prevent stack overflow.
Suggestion: Simplify recursive logic. The recursion limit is fixed at 2000 in this build; for larger iterations use multiple smaller batches.
Location: <source location of the recursive call>
```

### 10.3 Distinguishing the two errors

The error messages differ in the limit value (100000 vs 2000) and the phrasing ("per call chain" vs "fixed at"). Developers can identify which limit was hit from the message.

---

## 11. Performance Implications

| Metric | Current (Option A) | Proposed (Option C) | Delta |
|--------|--------------------|--------------------|-------|
| Per-chain overhead | 0 | 1 save + 1 restore of int | ~0 |
| Memory per chain | 0 | 1 int (28 bytes) | ~0 |
| Trampoline loop iterations | Same | Same | 0 |
| `_call_function` overhead | Same | Same | 0 |

**Assessment: negligible.** The save/restore of a single integer is O(1) and does not affect measurable performance.

---

## 12. Compatibility Implications

### 12.1 Backward compatibility

Programs that previously failed at ~500 records (due to cumulative budget) will now succeed. This is a **behavioral improvement**, not a regression. No existing valid program will fail that previously succeeded.

Programs that relied on the cumulative budget to catch infinite recursion will still be caught — each chain is independently bounded at 100,000 iterations.

### 12.2 ADR-017 compatibility

ADR-017 §7.5 requires: "All existing tests must pass with byte-identical output (determinism guard)."

Option C preserves byte-identical output because:
- The trampoline loop is unchanged
- `_call_function` is unchanged
- `_execute_block` is unchanged
- Only `_inline_tail_chain` gains save/restore logic
- The save/restore does not affect the iteration count within the chain (it only isolates chains from each other)

### 12.3 Language surface

No grammar, AST, IR, type checker, formatter, LSP, CLI, or stdlib changes. The fix is entirely within `interpreter.py`.

---

## 13. Test Strategy

### 13.1 Regression tests

| Test | What | Expected |
|------|------|----------|
| Sequential workloads | `deep_scalar(50000)` then `deep_list(60000)` | Both pass (previously second failed) |
| Multi-pass pipeline | 1000-record build/validate/sum | All passes complete |
| Single chain limit | `deep_scalar(150000)` | RuntimeError at 100k iterations |
| Mutual recursion | `f → g → f` infinite | RuntimeError |
| Tail recursion | `countdown(10000)` | Correct output |
| Determinism | 3 runs of canonical workload | Byte-identical output |
| Existing test suite | Full corpus | 0 regressions |

### 13.2 Acceptance criteria (from task specification)

| # | Criterion | Verification |
|---|-----------|-------------|
| AC-1 | 50k + 60k sequential workloads no longer fail | `deep_scalar(50000)` + `deep_list(60000)` both pass |
| AC-2 | Infinite recursion remains bounded | `f(n) { return f(n-1) }` hits RuntimeError |
| AC-3 | Mutual recursion remains bounded | `f → g → f` infinite hits RuntimeError |
| AC-4 | Tail recursion remains deterministic | 3 runs of `countdown(10000)` produce identical output |
| AC-5 | 10k canonical workload passes | `ail run` on canonical 10k workload succeeds in <5s |
| AC-6 | Existing valid programs retain behavior | Full test suite passes with 0 regressions |
| AC-7 | Error message identifies correct limit | Error says "100000 iterations per call chain" not "limit: 2000" |
| AC-8 | No grammar/AST/IR/stdlib/API changes | Diffs confined to `interpreter.py` |

---

## 14. Migration Implications

### 14.1 For existing programs

No migration required. Programs that previously failed at ~500 records will now succeed. Programs that worked before will continue to work.

### 14.2 For documentation

Update:
- `docs/reference/LANGUAGE_SPEC.md` — document per-chain iteration budget
- `docs/reference/STDLIB_REFERENCE.md` — add note about recursion limits
- `docs/guides/GETTING_STARTED.md` — add troubleshooting entry for recursion limits
- Error message text in `interpreter.py` — update to reference correct limit

### 14.3 For developers

Developers who previously used batching workarounds (e.g., processing 500 records at a time) can now process larger batches. The per-chain budget of 100,000 iterations supports workloads up to ~100,000 records per function call.

---

## 15. Rejection Rationale for Alternatives

| Option | Reason for rejection |
|--------|---------------------|
| A (status quo) | Fails I-4 (10k workload) and I-7 (error reporting). Cumulative budget blocks legitimate multi-pass pipelines. |
| B (reset per top-level) | "Top-level workload" is not a well-defined concept in AILang's execution model. The boundary between independent workloads is ambiguous. Mutual recursion across workloads would not be caught. |
| D (hybrid) | Marginally stronger safety at the cost of increased complexity. The trampoline loop's existing check provides sufficient global runaway protection. Option C is simpler and equally safe. |
| E (other) | Not required — Option C satisfies all invariants. |

---

## 16. Acceptance Criteria

The implementation is accepted when all of the following are true:

1. **AC-1:** `deep_scalar(50000)` + `deep_list(60000)` sequential workloads both pass
2. **AC-2:** `f(n) { return f(n-1) }` infinite recursion hits RuntimeError
3. **AC-3:** `f → g → f` mutual recursion hits RuntimeError
4. **AC-4:** `countdown(10000)` produces byte-identical output across 3 runs
5. **AC-5:** Canonical 10k workload passes in <5s
6. **AC-6:** Full test suite passes with 0 regressions
7. **AC-7:** Error message says "100000 iterations per call chain"
8. **AC-8:** Diffs confined to `interpreter.py` (plus documentation)

---

## 17. Implementation Scope (Planning Only)

### 17.1 Code changes

| File | Change | Lines |
|------|--------|-------|
| `compiler/runtime/interpreter.py` | Add save/restore with try/finally in `_inline_tail_chain` | ~8 lines |
| `compiler/runtime/interpreter.py` | Update error message in `_inline_tail_chain` | ~2 lines |
| `compiler/runtime/interpreter.py` | Update error message in `_trampoline_call` | ~2 lines |

### 17.2 Documentation changes

| File | Change |
|------|--------|
| `docs/reference/LANGUAGE_SPEC.md` | Document per-chain iteration budget |
| `docs/reference/STDLIB_REFERENCE.md` | Add recursion limits section |
| `docs/guides/GETTING_STARTED.md` | Add troubleshooting entry |

### 17.3 Test changes

| File | Change |
|------|--------|
| New test file | Sequential workload test (AC-1) |
| New test file | Infinite recursion test (AC-2) |
| New test file | Mutual recursion test (AC-3) |
| New test file | Determinism test (AC-4) |

---

## 18. Rollback Strategy

| Condition | Action |
|-----------|--------|
| Any existing test fails | Revert the save/restore change; investigate |
| Determinism regression | Revert; byte-identical output is non-negotiable |
| Performance regression (>10% on canonical workload) | Revert; measure overhead of save/restore |
| Error message is confusing | Update message text; no revert needed |

**Rollback mechanism:** The change is 4 lines in `_inline_tail_chain`. Reverting means removing the save/restore. The trampoline loop and `_call_function` are unchanged.

---

## 19. Approval Required

| Approver | Scope | Status |
|----------|-------|--------|
| Project owner | ADR acceptance | PENDING |
| Architecture reviewer | Design correctness | PENDING |

---

## 20. Summary

**Recommended:** Option C — per-call-chain budget.

**Why it is superior:**
- Simplest correct solution (8 lines of code in interpreter.py)
- Satisfies all 8 acceptance criteria
- Preserves all safety mechanisms (infinite recursion, mutual recursion, determinism)
- Improves backward compatibility (programs that failed at ~500 records now succeed)
- No language surface, API, or architecture changes
- Compatible with ADR-017

**What remains uncertain:**
- Whether the trampoline loop's own limit (line 474) needs adjustment after per-chain isolation (analysis suggests it does not — it provides adequate global protection)
- Whether documentation updates need CTO review

**Exact authorization required for implementation:**
- ADR acceptance by project owner
- Permission to modify `compiler/runtime/interpreter.py`
- Permission to add regression tests
- Permission to update documentation

**Files inspected:**
- `compiler/runtime/interpreter.py` (lines 100–572, 790–826)
- `compiler/runtime/sandbox.py` (lines 1–121)
- `docs/adr/ADR-017-gate-f-iteration-execution-model.md` (full)
- `docs/roadmap/AILANG_A101_ENGINEERING_HARDENING_PLAN.md` (full)
- `docs/roadmap/AILANG_A101_FINDING_RECONCILIATION.md` (full)
- `docs/roadmap/AILANG_A101_PHASE0_REPRODUCTION.md` (full)
- `docs/roadmap/AILANG_A101_DELIVERABLE_REPORT.md` (full)

**Files changed (must be only the ADR):**
- `docs/adr/ADR-018-cumulative-iteration-budget.md` — NEW
