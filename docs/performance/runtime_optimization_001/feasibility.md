# Optimization Feasibility Study

## Evaluation Framework

Each optimization is evaluated against profiler data only. No
optimization is recommended without measurement support.

**Scale:**
- **Gain:** Estimated runtime reduction based on profiler evidence
- **Complexity:** Lines of code changed, architectural impact
- **Risk:** Regression or correctness risk
- **Priority:** 1 (highest) to 5 (lowest)

---

## 1. Variable Lookup Caching

### Evidence

`Environment.resolve` accounts for 85.5% of the static analyzer's
runtime. The same names are resolved repeatedly — `length` is resolved
178,852 times in a single run, always finding it in the same scope
(the stdlib string module).

### Approach

After resolving `name` successfully, cache the mapping
`(environment_id, name) → resolved_environment` so subsequent lookups
of the same name from the same scope skip the chain traversal.

Two levels of caching:

1. **Per-frame cache:** Cache `name → value` in the current StackFrame
   after first resolution. Invalidated when the frame is popped.
2. **Per-environment cache:** Cache `name → target_environment` in each
   Environment after successful resolution through the parent chain.

### Estimated Gain

- **85-95% reduction in Environment.resolve calls** (from 1.6M to
  ~80K-240K) → **~73-81% overall runtime reduction**
- For the static analyzer: **359s → ~68-97s** (4-6x faster)
- For dice_roller: **0.100s → ~0.054s** (1.85x faster)

### Implementation Complexity

**Low.** ~20 lines of Python. Add a `_cache: dict[str, Any]` dict to
`Environment`, check it before chain traversal, populate it after
successful resolution.

For per-frame caching, add a `_resolve_cache` dict to `StackFrame`,
check on `StackFrame.resolve`, populate on miss.

### Risk

**Low.** Caching does not change semantics. The only concern is cache
invalidation if a variable is redefined in an inner scope that shadows
an outer one. The per-frame cache is safe because variables cannot be
redefined in the same scope (AILang forbids `let x = ...; let x = ...`).

The per-environment cache must account for inner-scope shadowing:
if child defines `x`, a lookup starting from parent should still find
the parent's `x`. This is the standard lexical scoping behavior.
A simple solution: only cache `name → environment` pairs where the
resolution stops at a given environment. If a child environment defines
the same name, it won't be in the parent's cache.

### Verdict

**Recommended. Priority 1. Highest ROI.**

---

## 2. String Operation Optimization

### Evidence

| Operation | Calls | Time | % Runtime |
|-----------|------:|-----:|----------:|
| `str.split` | 76,924 | 0.467s | 0.13% |
| `string.substring` | 43,581 | 0.218s | 0.06% |
| `string.length` | 178,852 | negligible | <0.01% |
| `string.equals` | 105,476 | negligible | <0.01% |
| `isinstance` | 11,024,668 | 0.599s | 0.17% |

String operations are collectively <0.2% of runtime. Optimizing them
would produce no measurable improvement.

### Estimated Gain

<0.2% runtime reduction.

### Complexity

Medium (would require native implementation or specialization).

### Risk

High (correctness of string semantics).

### Verdict

**Not recommended.** Negligible potential gain.

---

## 3. Interpreter Dispatch Optimization

### Evidence

`_evaluate_expression` uses a chain of `isinstance` checks to dispatch
expression evaluation. This accounts for 3.03% of runtime.

`_execute_node` uses a similar chain. This accounts for 0.99% of
runtime.

### Approach

Replace isinstance chains with:
- A `dispatch_id` integer attribute on each IR node
- A dispatch table (`list` or `dict`) mapping dispatch_id → handler

This replaces `isinstance(node, BinaryOperationIR)` (which calls
CPython's MRO search) with `handlers[node.dispatch_id](node)` (direct
list index).

### Estimated Gain

**~2-3% overall runtime reduction.** The isinstance chain is not
expensive enough to justify more aggressive approaches.

### Complexity

Low. Add a `dispatch_id` field to IRNode base class (~5 lines), convert
each isinstance check to a table lookup (~20 lines).

### Risk

Low. No semantic change.

### Verdict

**Nice-to-have. Priority 4.**

---

## 4. Tail Call Optimization (TCO)

### Evidence

From Phase 1 profiling: max_depth=385, avg_depth=143.7 for the
static analyzer on a 250-line target.

From Phase 2 profiling: `_call_function` accounts for 2.05% of runtime
(not a top hotspot).

The deep recursion is caused by mutually recursive functions
(`count_fn_calls_specific_inner`, `compute_source_stats_inner`, etc.)
where each function processes one element and recurses for the rest.
These tail-call to themselves.

### Approach

Detect tail-call position (return `f(...)` or `return expr` where
`expr` is a call). When a tail call is detected:
1. Pop current frame
2. Reuse the frame for the called function
3. Jump instead of call

This eliminates the stack frame creation for tail calls and prevents
unbounded stack growth.

### Estimated Gain

**~2% runtime reduction** (from `_call_function` + `StackFrame.__init__`
overhead). The main benefit is eliminating stack overflow for very deep
recursion, not raw speed.

For very deep recursion (depth > 1000), TCO would also avoid CPython's
recursion limit.

### Complexity

**Medium-High.** Requires:
1. Tail-call detection in the interpreter (identify "call in return
   position")
2. Frame reuse logic (pop before push)
3. Handling of mutually recursive tail calls (not just self-recursive)

### Risk

Medium. Must correctly handle:
- Parameter evaluation before frame pop
- Exception tracebacks
- Debugger integration

### Verdict

**Not recommended for speed. Could be justified for stack-depth safety.**
Priority 5 for performance, Priority 2 for correctness (prevents
recursion limit errors).

---

## 5. Trampolining

### Evidence

Same as TCO — deep recursion is the only justification.

### Approach

Replace direct function calls with return of a thunk `(function, args)`.
A top-level trampoline loop drives execution:

```python
def trampoline(self, fn, args):
    result = self._call_function(fn, args)
    while isinstance(result, Thunk):
        result = self._call_function(result.fn, result.args)
    return result
```

### Estimated Gain

**Negative or neutral.** Trampolining adds a dispatch loop per call.
For a 230-million-call workload, the trampoline overhead would likely
_increase_ runtime.

### Complexity

**High.** Requires converting the entire interpreter to continuation-
passing style, or at least all call sites.

### Risk

High. Major architectural change with many edge cases.

### Verdict

**Not recommended.** Overhead outweighs benefits. TCO is strictly
better for the same use case.

---

## 6. Bytecode VM

### Evidence

The current AST-walking interpreter spends ~3% of runtime in
`_execute_node` dispatch and ~3% in `_evaluate_expression` dispatch.
These are the dispatch overheads that a bytecode VM would eliminate.

However, the dominant cost (85.5%) is variable resolution, which a
bytecode VM would NOT eliminate unless combined with lexical addressing.

### Approach

Replace AST-walking with:
1. A bytecode compiler (IR → bytecode)
2. A register-based or stack-based VM

Each IR node becomes 1-3 bytecode instructions. Dispatch becomes a
single `switch(opcode)` in a tight loop.

### Estimated Gain

**~5-8% runtime reduction** from faster dispatch. A bytecode VM is
approximately 2-3x faster than an AST walker for the dispatch portion,
but dispatch is only ~6% of current runtime.

Without lexical addressing for variable resolution, the gain is limited
to ~5-8%.

### Complexity

**Very High.** Requires:
- Bytecode instruction set design
- Bytecode compiler (IR → bytecode)
- Bytecode VM with operand stack / registers
- Debug info mapping

Estimated 2,000-3,000 lines of code.

### Risk

High. Major architectural change. Bytecode VM bugs are notoriously
subtle (stack underflow, type confusion, etc.).

### Verdict

**Not recommended without lexical addressing.** If paired with lexical
addressing (making variable resolution O(1)), the combined gain could
be ~80-85%, justifying the complexity. The bytecode VM alone does not.

**Priority 5** (standalone), **Priority 2** (combined with lexical
addressing).

---

## 7. Host Language Rewrite (Rust, Go, etc.)

### Evidence

The 85.5% bottleneck is in `Environment.resolve` — a simple recursive
function that does dict lookups and parent-chain traversal. This is
algorithmic, not language-specific.

A Rust or Go rewrite would:
- Eliminate Python function call overhead (~55% of the 85.5%)
- Faster dict lookups via native hash maps
- Better memory locality
- No GIL

### Estimated Gain

**~3-5x raw speedup** from language change alone (lower-bound estimate
based on typical CPython vs Rust/Go benchmarks for hash-map-heavy
workloads).

If combined with caching and lexical addressing: **~20-50x** overall.

### Complexity

**Extremely High.** Complete rewrite of the entire compiler, stdlib,
and runtime. Estimated 15,000-25,000 lines of Rust/Go.

### Risk

Extreme. Entire codebase is replaced. Ecosystem (stdlib, tooling, LSP)
must be rebuilt or re-validated.

### Verdict

**Not recommended at current scale.** AILang is still experimental.
The ROI does not justify a rewrite until the language is proven and
performance demand is confirmed by real users.

**Priority 5.**

---

## Optimization Priority Matrix

| Priority | Optimization | Est. Gain | Complexity | Risk |
|:--------:|--------------|:---------:|:----------:|:----:|
| **1** | Variable lookup caching | **73-81%** | Low | Low |
| 2 | TCO (for correctness) | 2% | Medium | Medium |
| 3 | Bytecode VM + lexical addressing | 80-85% | Very High | High |
| 4 | Interpreter dispatch tuning | 2-3% | Low | Low |
| 5 | String optimization | <0.2% | Medium | High |
| 5 | Trampolining | Negative | High | High |
| 5 | Host language rewrite | 3-5x | Extreme | Extreme |

---

## Recommended Action

1. **Implement variable lookup caching.** This is the single highest-ROI
   optimization with minimal risk and complexity.
2. **Re-profile after caching.** Measure the remaining bottlenecks.
3. **Evaluate TCO only if recursion depth limit is hit.**
4. **Revisit bytecode VM + lexical addressing only if caching is
   insufficient.**
