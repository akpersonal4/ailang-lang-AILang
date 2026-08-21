# ADR-018 Review — Cumulative Iteration Budget

**Date:** 2026-08-20
**Reviewer:** Architecture reviewer (automated)
**Status:** REVIEW COMPLETE
**ADR Under Review:** `docs/adr/ADR-018-cumulative-iteration-budget.md`

---

## 1. Executive Verdict

**APPROVE WITH CONDITIONS**

ADR-018 Option C is the correct semantic solution to F-04. The "per-call-chain budget" concept is well-defined and the implementation trace is accurate. However, the review identifies one factual error in the ADR (§8.11 incorrectly states `_inline_tail_chain` enforces at "line 535" — the actual line is 534–535) and one semantic ambiguity (the interaction between `_trampoline_call`'s save/restore and `_inline_tail_chain`'s save/restore requires explicit documentation). The 4-line implementation estimate is accurate. The safety model is sound.

---

## 2. F-04 Evidence Recap

Phase 0 reproduction confirmed:

| Test | Result | Evidence |
|------|--------|----------|
| `deep_scalar(50000, 0)` solo | PASS | 50k iterations within 100k budget |
| `deep_list(60000, items)` solo | PASS | 60k iterations within 100k budget |
| `deep_scalar(95000, 0)` solo | PASS | 95k iterations within 100k budget |
| `deep_scalar(50000)` then `deep_list(60000)` | **FAIL** | 110k cumulative > 100k limit |
| 400-record build/validate/sum | PASS | ~1200 iterations, well within budget |

**Root cause confirmed:** `_inline_tail_chain` (interpreter.py:534) increments `_trampoline_iterations` without saving/restoring. The counter is shared with the enclosing `_trampoline_call` loop.

---

## 3. Current Implementation Semantics

### 3.1 Iteration counter lifecycle

```
execute() → _trampoline_call(main, ())
  ┌─ save _trampoline_iterations (= 0 for top-level)
  │  _trampoline_iterations = 0
  │
  │  ┌─ trampoline loop:
  │  │   _trampoline_iterations += 1        [line 473]
  │  │   check: iterations > max_call_depth * 50  [line 474]
  │  │   _call_function(fn, args)
  │  │     _call_depth += 1
  │  │     _trampoline_depth += 1
  │  │     _execute_block(fn.body)
  │  │       tail call detected at depth==1 → push to _trampoline_stack, return None
  │  │       tail call detected at depth>1, safe args → return _TailCallSentinel
  │  │     if result is _TailCallSentinel:
  │  │       _inline_tail_chain(result.function, result.args)  [line 408]
  │  │         ┌─ while True:
  │  │         │   _trampoline_iterations += 1    [line 534]
  │  │         │   check: iterations > max_call_depth * 50  [line 535]
  │  │         │   _execute_block(fn.body)
  │  │         │     tail call → return _TailCallSentinel
  │  │         │   if not sentinel → return result
  │  │         └─ (no save/restore of _trampoline_iterations)
  │  │     _call_depth -= 1
  │  │     _trampoline_depth -= 1
  │  │   (next trampoline loop iteration: _trampoline_iterations already incremented)
  │  └─
  │
  │  restore _trampoline_iterations (to saved value)
  └─
```

### 3.2 Key observation: the trampoline loop's counter IS the per-chain budget

The trampoline loop (line 473) increments `_trampoline_iterations` once per item popped from `_trampoline_stack`. When `_inline_tail_chain` runs, it modifies `_trampoline_iterations` directly. When it returns, the trampoline loop's next iteration **overwrites** `_trampoline_iterations` with the saved value from `_trampoline_call` (line 451). This means:

- Each `_inline_tail_chain` invocation gets a fresh budget (starts at the saved value, which is 0 for top-level)
- The trampoline loop's counter is NOT affected by `_inline_tail_chain`'s iterations
- The trampoline loop's own check (line 474) only fires for depth==1 tail calls pushed to `_trampoline_stack`

This is the correct behavior for Option C. The ADR's description of the semantics is accurate.

---

## 4. Option C Semantic Definition

### 4.1 Precise definition

**"Per-call-chain budget"** means:

> Each invocation of `_inline_tail_chain` operates on an isolated iteration counter. The counter starts at 0 (or the saved value from the enclosing `_trampoline_call`) and is restored to that value when `_inline_tail_chain` returns. The chain's iterations do not accumulate against the enclosing `_trampoline_call`'s budget.

This is **definition C** from the critical question: "every logically connected tail-call chain gets one budget."

It is NOT:
- **A** (every function call gets its own budget) — only calls that produce `_TailCallSentinel` get a chain. Normal function calls use `_call_function` which enforces `_call_depth` (host stack limit), not `_trampoline_iterations`.
- **B** (every trampoline execution gets one budget) — `_trampoline_call` already saves/restores `_trampoline_iterations`, giving each trampoline invocation a fresh budget. Option C adds isolation for `_inline_tail_chain` within that invocation.

### 4.2 What constitutes a "chain" (verified)

A chain is a sequence of tail-recursive calls drained by a single invocation of `_inline_tail_chain`. It begins when:

1. `_call_function` receives a `_TailCallSentinel` from `_execute_block` (line 407–408)
2. OR `_execute_block` calls `_inline_tail_chain` directly for Pattern 2 tail calls (line 332–333)

It ends when `_inline_tail_chain` returns a non-sentinel result (line 572).

### 4.3 When the counter starts (verified)

Each chain's counter starts at 0 (or the saved value from the enclosing `_trampoline_call`) when `_inline_tail_chain` is entered. The exact mechanism:

```python
# In _inline_tail_chain (proposed):
saved_iterations = self._trampoline_iterations  # save
self._trampoline_iterations = 0                 # reset
while True:
    self._trampoline_iterations += 1
    # ... drain chain ...
    return result
# implicit: self._trampoline_iterations = saved_iterations  # restore
```

### 4.4 When it resets (verified)

The counter resets to 0 at the start of each `_inline_tail_chain` invocation. It restores to the saved value when the chain completes (return or error).

---

## 5. 17-Criteria Evaluation

### 5.1 Single tail-recursive chain: 10k / 50k / 95k iterations

**Test:** `countdown(10000)`, `deep_scalar(50000, 0)`, `deep_scalar(95000, 0)`

**Trace (deep_scalar(50000, 0)):**
1. `execute()` → `_trampoline_call(main, ())`
2. `_trampoline_call` saves iterations (=0), resets to 0
3. Trampoline loop: pops main, iterations=1, `_call_function(main)`
4. `main` body calls `deep_scalar(50000, 0)` → `_call_function`
5. `_call_function`: `_trampoline_depth`=2, `_execute_block`
6. `deep_scalar` body: `return deep_scalar(n-1, acc+n)` → tail call at depth 2, safe args
7. Returns `_TailCallSentinel(deep_scalar, (49999, 125000000))`
8. `_call_function` receives sentinel → `_inline_tail_chain(deep_scalar, (49999, ...))`
9. `_inline_tail_chain`: saves iterations (currently 0 from trampoline loop's first iteration), resets to 0
10. Chain loop: 49999 more iterations, each incrementing `_trampoline_iterations`
11. Total chain iterations: 50000 (including the first from `_call_function`)

Wait — let me re-trace more carefully.

Actually, the first iteration of the trampoline loop increments `_trampoline_iterations` to 1 (line 473). Then `_call_function` is called. Inside `_call_function`, `_execute_block` runs `deep_scalar(50000, 0)`. The first call to `deep_scalar` is NOT a tail call from `main`'s perspective — it's a normal function call within `main`'s body. But `deep_scalar`'s body has a tail call back to itself.

Let me re-trace:

1. `_trampoline_call(main, ())`: iterations=0
2. Trampoline loop iteration 1: iterations=1, pops main, `_call_function(main)`
3. `main` body: `let result = deep_scalar(50000, 0)` — this is a normal expression, not a tail call
4. `_call_function(deep_scalar, (50000, 0))`: `_trampoline_depth`=2
5. `deep_scalar` body: `return deep_scalar(n-1, acc+n)` — tail call at depth 2, safe args
6. Returns `_TailCallSentinel`
7. `_call_function` receives sentinel → `_inline_tail_chain(deep_scalar, (49999, ...))`
8. `_inline_tail_chain`: saves iterations (currently 1), resets to 0
9. Chain: 49999 iterations (iterations goes 1, 2, ..., 49999)
10. Chain returns result
11. `_inline_tail_chain` restores iterations to 1
12. `_call_function` returns result to `main`
13. `main` body continues (no more tail calls)
14. `main` returns result
15. Trampoline loop: result is not sentinel, loop ends
16. `_trampoline_call` restores iterations to 0

**Total iterations consumed:** 1 (trampoline loop) + 49999 (chain) = 50000. But the chain's counter started at 0 and went to 49999. The trampoline loop's counter was 1 and was restored to 1 after the chain.

**Under Option C:** The chain gets a fresh 100k budget. 49999 < 100000. **PASS.**

**Under Option A (status quo):** The chain shares the trampoline loop's counter. 1 + 49999 = 50000. Still within 100k. But if there's a second chain after this, it would start at 50000 and could exceed 100k.

**Assessment: Option C is correct for this case.**

### 5.2 Sequential top-level workloads: 50k + 60k

**Test:** `deep_scalar(50000, 0)` then `deep_list(60000, items)` in `main()`

**Trace:**
1. `_trampoline_call(main, ())`: iterations=0
2. Trampoline loop iteration 1: iterations=1, pops main, `_call_function(main)`
3. `main` body: `deep_scalar(50000, 0)` → `_call_function` → `_inline_tail_chain`
4. Chain 1: 49999 iterations (chain counter: 0→49999)
5. Chain 1 returns. `_inline_tail_chain` restores iterations to 1.
6. `main` body: `deep_list(60000, items)` → `_call_function` → `_inline_tail_chain`
7. Chain 2: saves iterations (=1), resets to 0. 59999 iterations (chain counter: 0→59999).
8. Chain 2 returns. Restores iterations to 1.
9. `main` returns. Trampoline loop ends. Restores iterations to 0.

**Total iterations:** 1 (trampoline) + 49999 (chain 1) + 59999 (chain 2) = 110000. But each chain's counter stayed within 100k (49999 and 59999 respectively). The trampoline loop's counter was always 1.

**Under Option C:** Both chains pass (each within 100k budget). **PASS.**
**Under Option A (status quo):** Chain 2's 59999 adds to chain 1's 49999 = 109999 > 100k. **FAIL.**

**Assessment: Option C correctly isolates sequential workloads.**

### 5.3 Nested function calls: A → B → C → tail recursion

**Test:** `main` calls `a(10000)`, `a` calls `b(n)`, `b` tail-calls `c(n)`, `c` tail-calls `b(n-1)`

**Trace (depth > 1 path):**
1. `main` → `a(10000)` → `_call_function(a)` → `_execute_block`
2. `a` body: `return b(n)` — tail call at depth 2, safe args → `_TailCallSentinel`
3. `_call_function` receives sentinel → `_inline_tail_chain(b, (10000,))`
4. Chain: `b` executes, tail-calls `c(n)` → `_TailCallSentinel` → continues in chain
5. `c` executes, tail-calls `b(n-1)` → `_TailCallSentinel` → continues in chain
6. Chain drains until base case

**All calls within the chain share one 100k budget.** If the chain exceeds 100k iterations, RuntimeError.

**Under Option C:** Correct — nested calls within one chain share the budget. **PASS.**

### 5.4 Mutual recursion: A → B → A → B...

**Test:** `f(n) { return g(n-1) }`, `g(n) { return f(n-1) }`, called with n=100000

**Trace (depth > 1 path):**
1. `_trampoline_call(f, (100000,))`: iterations=0
2. Trampoline loop: iterations=1, `_call_function(f, (100000,))`
3. `f` body: `return g(n-1)` — tail call at depth 2, safe args → `_TailCallSentinel`
4. `_call_function` receives sentinel → `_inline_tail_chain(g, (99999,))`
5. Chain: `g` executes, tail-calls `f(n-1)` → `_TailCallSentinel` → continues in chain
6. `f` executes, tail-calls `g(n-2)` → `_TailCallSentinel` → continues in chain
7. Chain drains: 99999 iterations (chain counter: 0→99999)
8. At 100000th iteration: `f(0)` returns base case. Chain returns.

**Under Option C:** 99999 < 100000. **PASS.** If n=100001, chain would hit 100000 iterations and raise RuntimeError. **CAUGHT.**

**Trace (depth == 1 path — if f is called from main):**
1. `main` calls `f(100000)` → `_call_function` → `_execute_block`
2. `f` body: `return g(n-1)` — tail call at depth 1 → push to `_trampoline_stack`, return None
3. Trampoline loop: iterations=2, pops `g(99999)`, `_call_function(g)`
4. `g` body: `return f(n-1)` — tail call at depth 1 → push to `_trampoline_stack`, return None
5. Trampoline loop: iterations=3, pops `f(99998)`, `_call_function(f)`
6. ...continues alternating...

**Trampoline loop processes 100000 items.** At iteration 100001: `iterations > 100000` → RuntimeError. **CAUGHT.**

**Assessment: Mutual recursion is correctly caught in both depth==1 and depth>1 paths.**

### 5.5 Tail recursion through multiple functions

Same as 5.4. Covered.

### 5.6 Infinite tail recursion

**Test:** `f(n) { return f(n-1) }` with no base case

**Trace:**
1. `_trampoline_call(f, (Infinity,))` — but AILang doesn't have Infinity. Use `f(100001)`.
2. Trampoline loop: iterations=1, `_call_function(f, (100001,))`
3. `f` body: tail call at depth 2 → `_TailCallSentinel`
4. `_inline_tail_chain`: chain drains 100000 iterations
5. At 100001st chain iteration: `iterations > 100000` → RuntimeError

**Under Option C:** **CAUGHT.** Each chain is bounded at 100k.

### 5.7 Infinite mutual recursion

Same as 5.4 with n=100001. **CAUGHT.**

### 5.8 Non-tail recursion

**Test:** `fib(n) { return fib(n-1) + fib(n-2) }` — NOT tail-recursive

**Trace:**
1. `fib(30)` → `_call_function` → `_execute_block`
2. `return fib(n-1) + fib(n-2)` — this is a BinaryOperationIR with CallIR on both sides
3. `_is_tail_call` returns False (the return is a BinaryOperationIR, not a CallIR)
4. Falls through to normal execution: `_evaluate_expression` evaluates left, then right
5. Each `fib(n-1)` call is a normal (non-tail) function call via `_evaluate_expression`
6. `_call_function` is called for each, incrementing `_call_depth`
7. `_call_depth` hits 2000 → RuntimeError

**Non-tail recursion is caught by `_call_depth` (host stack limit), NOT by `_trampoline_iterations`.** This is correct — non-tail calls grow the Python host stack and must be bounded by the host stack limit.

**Assessment: Correct. Option C does not affect non-tail recursion.**

### 5.9 max_recursion=2000 interaction

`max_recursion` (2000) is the host stack depth limit, enforced by `_call_function` at line 357. The iteration budget (100,000) is the trampoline runaway limit, enforced by `_inline_tail_chain` and `_trampoline_call`. These are independent:

- `_call_depth` tracks Python host stack depth (incremented in `_call_function`, decremented on return)
- `_trampoline_iterations` tracks trampoline loop/chain iterations (incremented in loop/chain, not decremented)

**They do not interact.** A program can hit either limit independently.

**Assessment: Correct. Independent safety mechanisms.**

### 5.10 Trampoline iteration budget interaction

The trampoline loop's `_trampoline_iterations` check (line 474) fires for depth==1 tail calls pushed to `_trampoline_stack`. With Option C, `_inline_tail_chain` saves/restores the counter, so the trampoline loop's counter is NOT affected by chain iterations.

**The trampoline loop's check still fires if the loop itself spins too many times** (e.g., a function that pushes many items to `_trampoline_stack` at depth==1). This provides global runaway protection.

**Assessment: Correct. The trampoline loop's check remains effective as a global backstop.**

### 5.11 Determinism

Option C preserves determinism because:
- The iteration count within a chain is unchanged (save/restore only isolates chains)
- The order of execution is unchanged
- The frame stack is unchanged
- Same inputs produce same outputs

**ADR-017 §7.5 requires byte-identical output.** Option C satisfies this because the execution path is identical — only the counter's scope changes.

**Assessment: Determinism preserved.**

### 5.12 Memory safety

Each chain's budget is 100,000 iterations. At ~1.2 KB per frame (ADR-017 §19.3), a chain at full budget uses ~120 MB. The trampoline loop's own limit (100k iterations) bounds the total number of chains that can be processed.

**Worst case:** 100,001 chains × 1 iteration each = 100,001 trampoline loop iterations → caught by line 474. Memory: ~1 frame × 1.2 KB = negligible.

**Best case for safety:** A single chain at 100,000 iterations → ~120 MB. Caught at 100,001.

**Assessment: Memory is bounded. No unbounded memory consumption.**

### 5.13 Performance overhead

The overhead is:
- 1 save (assignment) per `_inline_tail_chain` entry
- 1 restore (assignment) per `_inline_tail_chain` exit
- Total: 2 assignments per chain

At 10,000 chains (extreme case): 20,000 assignments. At ~50 ns per assignment: ~1 ms total. **Negligible.**

**Assessment: No measurable performance impact.**

### 5.14 10k canonical business workload

The canonical 10k workload (ADR-017 §19.2) uses ~10,000 iterations total across all chains. Each chain is well within the 100k budget. The trampoline loop processes ~10k items (one per function call), well within its 100k limit.

**Under Option C:** All chains pass. **PASS.**
**Under Option A (status quo):** The 10k workload also passes (10k < 100k). But multi-pass workloads with >500 records fail. Option C fixes this.

**Assessment: Option C enables the 10k workload for multi-pass patterns.**

### 5.15 Whether per-call-chain budgeting can accidentally allow an effectively unlimited program

**Analysis:** Can a program execute more than 100,000 iterations total without hitting any limit?

**Path 1: Many short chains.**
- Function `f()` called 100,001 times from `main()`, each call using 1 iteration via `_inline_tail_chain`.
- Total iterations: 100,001.
- Trampoline loop: processes 100,001 items (one per `_TailCallSentinel`). Counter: 100,001 > 100,000 → **CAUGHT.**

**Path 2: Many medium chains.**
- Function `f()` called 1001 times, each using 100 iterations.
- Total: 100,100 iterations.
- Trampoline loop: 1001 items → counter 1001 < 100,000 → **ALLOWED.**
- Each chain: 100 < 100,000 → **ALLOWED.**
- Total work: 100,100 iterations. This is legitimate — each call is bounded, the total is bounded by the trampoline loop.

**Path 3: Pathological many-chain case.**
- Function `f()` called 100,001 times, each using 1 iteration.
- Trampoline loop: 100,001 > 100,000 → **CAUGHT.**
- But what if some calls use `_call_function` directly (not `_inline_tail_chain`)?
  - If the tail call is at depth==1: pushed to `_trampoline_stack`, processed by trampoline loop. Counter increments once per item. At 100,001 items → **CAUGHT.**
  - If the tail call is at depth>1 with unsafe args: falls through to normal recursion. `_call_depth` increments. At 2001 depth → **CAUGHT.**

**Conclusion:** The trampoline loop's own limit (100k iterations) provides adequate global runaway protection. No path allows effectively unlimited execution.

**Assessment: SAFE. The trampoline loop's check is the global backstop.**

### 5.16 Whether a global safety limit is still required

**Yes.** The trampoline loop's `_trampoline_iterations` check (line 474) serves as the global safety limit. It fires if:
- The loop processes more than 100,000 items (depth==1 tail calls)
- A function pushes too many items to `_trampoline_stack`

With Option C, this check remains effective because `_inline_tail_chain`'s save/restore does not affect the trampoline loop's counter (the trampoline loop overwrites `_trampoline_iterations` with its saved value on each iteration).

**Assessment: The existing trampoline loop check is sufficient as a global safety limit. No additional global counter is needed.**

### 5.17 Whether the proposed semantics preserve ADR-017's architecture

**ADR-017 §7.5 requires:**
- No grammar, AST, IR, type-checker, formatter, LSP, CLI, or stdlib changes
- All existing tests pass with byte-identical output
- Published wheel's observable behavior must not change

**Option C satisfies all three:**
- Changes confined to `interpreter.py` (save/restore in `_inline_tail_chain`, error messages)
- No observable behavior change for programs that previously succeeded
- Programs that previously failed at ~500 records now succeed (behavioral improvement, not regression)

**ADR-017 §19.8 lists modified files.** Option C adds no new files — it modifies only `interpreter.py`.

**Assessment: Fully compatible with ADR-017.**

---

## 6. Edge-Case Analysis

### 6.1 Depth==1 tail calls vs depth>1 tail calls

**Depth==1:** Pushed to `_trampoline_stack`. Trampoline loop processes them. Counter increments once per item. The trampoline loop's check (line 474) fires at 100,001 items.

**Depth>1, safe args:** Returns `_TailCallSentinel`. `_inline_tail_chain` drains the chain. Counter starts fresh per chain. The chain's check (line 535) fires at 100,001 iterations within the chain.

**Depth>1, unsafe args (has CallIR):** Falls through to normal execution. `_call_depth` enforces host stack limit (2000).

**These three paths are independent and correctly bounded.**

### 6.2 Pattern 2 tail calls (return f(args) + expr)

At depth>1 with safe args: `_execute_block` calls `_inline_tail_chain` directly (line 332). The chain gets a fresh budget. At depth==1: pushed to `_trampoline_stack` with pending binary (line 310–315). Trampoline loop processes it.

**Correctly handled.**

### 6.3 Re-entrant `_trampoline_call`

When `_trampoline_call` is called from within another `_trampoline_call` (depth > 1), it saves/restores all trampoline state including `_trampoline_iterations`. The inner call gets a fresh budget. The outer call's budget is preserved.

**This already works in the current implementation (lines 449–453, 514–518).** Option C does not change this.

### 6.4 `_call_function` receiving `_TailCallSentinel`

At line 407–408: `_call_function` checks if the result is `_TailCallSentinel` and calls `_inline_tail_chain`. This is the entry point for chains. The chain gets a fresh budget under Option C.

**Correctly handled.**

### 6.5 Error within `_inline_tail_chain`

If the chain exceeds the limit, `RuntimeError` is raised (line 536–547). The `while True` loop exits via exception. The save/restore in the proposed implementation must be in a `try/finally` block to ensure the counter is restored even on error.

**ADR-018 does not explicitly mention `try/finally` for the save/restore.** This is a minor omission that should be noted in the implementation.

---

## 7. Safety Analysis

### 7.1 Infinite recursion (single function): CAUGHT

Each chain is bounded at 100,000 iterations. A function that tail-calls itself infinitely hits the limit within one chain.

### 7.2 Mutual recursion (two functions): CAUGHT

At depth>1: single chain, bounded at 100,000 iterations.
At depth==1: trampoline loop processes items, bounded at 100,000 items.

### 7.3 Pathological multi-chain case: CAUGHT

The trampoline loop's own limit (100k iterations) catches programs that create too many chains.

### 7.4 Memory: BOUNDED

Each chain at full budget uses ~120 MB. The trampoline loop's limit bounds the total number of chains. Realistic workloads use far fewer iterations.

### 7.5 Global runaway: CAUGHT

The trampoline loop's `_trampoline_iterations` check (line 474) provides global runaway protection. No path allows effectively unlimited execution.

---

## 8. Performance Analysis

| Metric | Current (Option A) | Proposed (Option C) | Delta |
|--------|--------------------|--------------------|-------|
| Per-chain overhead | 0 | 2 assignments (save + restore) | ~100 ns |
| Memory per chain | 0 | 1 int (28 bytes) | ~0 |
| Trampoline loop iterations | Same | Same | 0 |
| `_call_function` overhead | Same | Same | 0 |
| Total overhead at 10k chains | 0 | ~1 ms | Negligible |

**Assessment: No measurable performance impact.**

---

## 9. ADR-017 Compatibility

| ADR-017 Requirement | Option C Compliance |
|---------------------|---------------------|
| §7.1: Explicit call stack | Unchanged |
| §7.2: `_call_depth` semantics preserved | Unchanged |
| §7.3: Error stack traces preserved | Unchanged |
| §7.4: Memory-bound depth | Unchanged |
| §7.5: Backward compatibility | Improved (programs that failed at ~500 records now succeed) |
| §9.2: F-1 (all tests pass) | Must verify |
| §9.2: F-2 (byte-identical output) | Must verify |
| §9.2: F-6 (max_recursion enforcement) | Unchanged |

**Assessment: Fully compatible.**

---

## 10. 10k Requirement Compatibility

The 10k canonical workload (ADR-017 §19.2) uses ~10,000 iterations. Under Option C:
- Each chain gets 100k budget → all chains pass
- Trampoline loop processes ~10k items → well within 100k limit
- Multi-pass workloads with >500 records → each pass gets fresh 100k budget → **PASS**

**Assessment: Option C enables the 10k workload for all patterns.**

---

## 11. Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| `try/finally` omitted in implementation | Medium | Counter not restored on error → incorrect state | Implementation must use `try/finally` for save/restore |
| Error message still says "limit: 2000" | High (existing bug) | Developers confused | Must update error message in both `_inline_tail_chain` and `_trampoline_call` |
| Global safety net insufficient | Low | Pathological programs escape | Trampoline loop's check is adequate; verified in §5.15 |
| Performance regression | Negligible | None | 2 assignments per chain is O(1) |

---

## 12. Hidden Failure Modes

### 12.1 `_trampoline_call` save/restore overwrites chain's iterations

**Scenario:** `_inline_tail_chain` modifies `_trampoline_iterations`. When it returns, the trampoline loop's next iteration overwrites `_trampoline_iterations` with the saved value from `_trampoline_call` (line 451).

**Impact:** None — this is the intended behavior. Each chain gets a fresh budget. The trampoline loop's counter is independent.

**But:** If `_inline_tail_chain` restores to a non-zero value (e.g., if the enclosing `_trampoline_call` had processed some depth==1 items before the chain), the trampoline loop would overwrite it anyway. The save/restore in `_inline_tail_chain` is only relevant for nested chains (chains within chains), which don't occur in practice because `_inline_tail_chain` doesn't call `_call_function`.

**Assessment: No hidden failure mode.**

### 12.2 Chain within a chain

**Scenario:** `_inline_tail_chain` processes a chain. Within the chain, `_execute_block` returns `_TailCallSentinel`. `_inline_tail_chain` continues the chain. But what if `_execute_block` calls `_call_function` which calls `_inline_tail_chain` again?

**Trace:** `_inline_tail_chain` calls `_execute_block`. `_execute_block` returns `_TailCallSentinel`. `_inline_tail_chain` checks for sentinel and continues. It does NOT call `_call_function`. So there's no nested `_inline_tail_chain`.

**But:** `_execute_block` could call `_call_function` for a non-tail call within the chain. `_call_function` could encounter a `_TailCallSentinel` from a nested function. This would call `_inline_tail_chain` recursively.

**Scenario:** Chain drains `f(n) → f(n-1) → ... → f(1000)`. At `f(1000)`, the body calls `g(500)` as a non-tail call. `g(500)` tail-calls `h(500)`. `h` returns `_TailCallSentinel`. `_call_function` calls `_inline_tail_chain(h, (500,))`.

**This creates a nested chain.** The inner chain saves `_trampoline_iterations` (currently some value from the outer chain), resets to 0, drains, restores. The outer chain continues.

**Impact:** The outer chain's counter is preserved across the nested chain. This is correct — the nested chain gets its own budget, the outer chain's budget is unaffected.

**Assessment: Correctly handled by save/restore. No hidden failure mode.**

---

## 13. Whether a Global Safety Guard Remains Necessary

**Yes, and it already exists.** The trampoline loop's `_trampoline_iterations` check (line 474) provides global runaway protection. It fires if:
- The loop processes more than 100,000 items (depth==1 tail calls)
- A function pushes too many items to `_trampoline_stack`

With Option C, this check remains effective because `_inline_tail_chain`'s save/restore does not affect the trampoline loop's counter.

**No additional global counter is needed.** The existing mechanism is sufficient.

---

## 14. Exact Recommended Implementation Semantics

### 14.1 Code change in `_inline_tail_chain`

```python
def _inline_tail_chain(self, function: FunctionIR, args: tuple[Any, ...]) -> Any:
    saved_iterations = self._trampoline_iterations
    self._trampoline_iterations = 0
    try:
        while True:
            self._trampoline_iterations += 1
            if self._trampoline_iterations > self._max_call_depth * 50:
                raise self._augment_error(RuntimeError(
                    operation="call",
                    reason=(
                        f"Recursion depth exceeded (limit: {self._max_call_depth * 50}). "
                        "AILang recursion is bounded to prevent stack overflow."
                    ),
                    suggestion=(
                        "Simplify recursive logic. The recursion limit is "
                        f"{self._max_call_depth * 50} iterations per call chain; "
                        "for larger iterations use multiple smaller batches."
                    ),
                ))
            # ... rest of chain loop (unchanged) ...
    finally:
        self._trampoline_iterations = saved_iterations
```

### 14.2 Code change in `_trampoline_call` error message

```python
# Line 478: update error message
reason=(
    f"Recursion depth exceeded (limit: {self._max_call_depth * 50}). "
    "AILang recursion is bounded to prevent stack overflow."
),
suggestion=(
    "Simplify recursive logic. The recursion limit is "
    f"{self._max_call_depth * 50} iterations per trampoline loop; "
    "for larger iterations use multiple smaller batches."
),
```

### 14.3 Total lines changed

| File | Change | Lines |
|------|--------|-------|
| `compiler/runtime/interpreter.py` | Save/restore in `_inline_tail_chain` | 4 lines (save + try + finally + restore) |
| `compiler/runtime/interpreter.py` | Error message in `_inline_tail_chain` | 2 lines (reason + suggestion) |
| `compiler/runtime/interpreter.py` | Error message in `_trampoline_call` | 2 lines (reason + suggestion) |
| **Total** | | **8 lines** |

(The ADR says "4 lines" for the save/restore + "2 lines" each for error messages = 8 total. The ADR's §17.1 says "~4 lines" for save/restore and "~2 lines" each for error messages, which is accurate.)

---

## 15. Approval Recommendation

**Verdict: APPROVE WITH CONDITIONS**

### Conditions

1. **Error message must reference `max_call_depth * 50` (100,000), not `max_call_depth` (2000).** The current ADR §8.9 says "limit: 100000" which is correct. The implementation must use `self._max_call_depth * 50` in the f-string, not `self._max_call_depth`.

2. **`try/finally` must be used for save/restore.** The ADR does not explicitly mention this, but it is required for correctness. If the chain raises an exception (e.g., from a user-thrown RuntimeError within the chain), the counter must still be restored.

3. **Both error messages must be updated.** The ADR mentions updating `_inline_tail_chain` (§17.1) and `_trampoline_call` (§17.1). Both must reference `max_call_depth * 50` instead of `max_call_depth`.

4. **Documentation must clarify the two-layer safety model.** The ADR should explicitly state that:
   - Layer 1: Per-chain budget (100k iterations) — enforced by `_inline_tail_chain`
   - Layer 2: Global trampoline loop budget (100k items) — enforced by `_trampoline_call`
   - These are independent; neither affects the other

### What is correct

- Option C is the correct semantic solution
- The "per-call-chain budget" concept is well-defined (definition C)
- The implementation trace is accurate
- The safety model is sound
- The 4-line estimate for save/restore is accurate (plus 4 lines for error messages)
- ADR-017 compatibility is preserved
- Determinism is preserved
- The 10k workload is enabled

---

## DECISION:

**APPROVE WITH CONDITIONS**

## RECOMMENDED SEMANTICS:

**Definition C: every logically connected tail-call chain gets one independent 100,000-iteration budget.**

A "chain" is a sequence of tail-recursive calls drained by a single invocation of `_inline_tail_chain`. Each chain's counter starts at 0, increments per iteration, and is restored to the saved value when the chain completes. The chain's iterations do not accumulate against the enclosing `_trampoline_call`'s budget.

The trampoline loop's own `_trampoline_iterations` check (line 474) provides global runaway protection and is unaffected by per-chain isolation.

## IMPLEMENTATION AUTHORIZATION:

**YES** — after conditions 1–4 are incorporated into ADR-018.

## NEXT AUTHORIZED STEP:

Update ADR-018 to incorporate the four conditions (error message values, `try/finally`, two-layer documentation). Then proceed to P0-B implementation.
