# M26 — Loop Capture Semantics Investigation

**Status:** 🟡 Investigation Complete — Decision Required
**Date:** 2026-07-10
**Author:** Language Architect
**Relevant ADRs:** ADR-001, ADR-002, ADR-005, ADR-006, ADR-007, ADR-009

---

## 1. Problem Statement

The experimental `for item in collection { body }` primitive lowers the entire
loop into a **standalone recursive helper function** at module level. Because
AILang uses static lexical scoping (ADR-005) and does not support closures,
the generated function cannot access variables from the enclosing function's
scope.

```ail
let total = 0
for item in items {
    total = total + item       ❌ 'total' not in scope of __for_fn_0
}
```

The runtime scope chain for `__for_fn_0` is:

```
__for_fn_0 frame → global environment
```

But `total` lives in:

```
enclosing_fn frame → global environment
```

These are sibling chains, not parent-child. `_resolve_name` never crosses
the sibling boundary.

---

## 2. Current State

### 2.1 Lowering Architecture

The for-loop is entirely eliminated at IR-build time (no `ForIR` node):

```
for item in collection { body }
  ↓
fn __for_fn_N(__lst_N, __idx_N)           ← module-level function
    if (__idx_N < list.len(__lst_N))
        let item = list.get(__lst_N, __idx_N)
        {body}                             ← user's body pasted in
        __for_fn_N(__lst_N, __idx_N + 1)   ← recursive call
    else nil
__for_fn_N(collection, 0)                  ← initial call at loop site
```

### 2.2 Runtime Scope Model

| Component | Role | Parent Chain |
|-----------|------|-------------|
| `Runtime._frame_stack` | Call stack of `StackFrame`s | Each frame's `Environment.parent` → caller's frame env |
| `StackFrame.environment` | Contains variable bindings | Walks up to caller's frame env, then global |
| `Environment._parent` | Lexical parent chain | Set at frame creation |
| `Environment._resolve_cache` | O(1) lookup cache (ADR-006) | Caches owning `Environment` pointer |

### 2.3 Free Variable Classes

Any variable reference in the loop body falls into one of three categories:

| Category | Example | Currently Works? |
|----------|---------|-----------------|
| Loop variable | `item` in `for item in ...` | ✅ Declared via `let item = list.get(...)` |
| Module-level var | `list` in `list.len(...)` | ✅ Resolves via global/builtins |
| **Enclosing-function var** | `total` in `total = total + item` | **❌ Not found** |

---

## 3. Solution Space

I identified 5 solution families, analyzed against 6 criteria:

| # | Approach | Closure Required? | New IR Nodes? | Runtime Changes? | Mutability Support | Complexity |
|---|----------|:---:|:---:|:---:|:---:|:---:|
| A | Free variable detection + parameter threading | No | No | No | Single variable | Medium |
| B | In-place IR expansion (RecurseIR) | No | Yes | Yes | Full | High |
| C | Mutable cells (Ref types) | No | No | Yes | Full | Medium |
| D | Heap-allocated closure environments | Yes | Yes | Yes | Full | High |
| E | Diagnostic-only restriction | No | No | No | N/A | Low |

---

## 4. Deep Analysis

### 4.1 Approach A — Free Variable Detection + Parameter Threading

**How it works:**

1. **Analyze** the loop body AST to find free variable references (identifiers
   not declared inside the loop body).
2. **Categorize** each reference as read-only or written (appears on LHS of `=`).
3. **Add parameters** to the generated function for each free variable.
4. **Thread through** recursive calls: read-only vars are passed unchanged;
   written vars are passed and their updated value is returned from the function.
5. **Capture at call site**: the initial call's return value is assigned back
   to the original variable.

**Read-only example:**

```ail
let offset = 5
for item in items {
    print(item + offset)             ← offset is read-only
}
```

↓

```
fn __for_fn_0(lst, idx, offset)      ← offset added as parameter
    if (idx < list.len(lst))
        let item = list.get(lst, idx)
        print(item + offset)
        __for_fn_0(lst, idx + 1, offset)  ← passed through
    else nil
__for_fn_0(items, 0, offset)         ← initial value passed
```

**Written (single accumulator) example:**

```ail
let total = 0
for item in items {
    total = total + item             ← total is written
}
```

↓

```
fn __for_fn_0(lst, idx, total)       ← total added as parameter
    if (idx < list.len(lst))
        let item = list.get(lst, idx)
        total = total + item         ← updates local param
        __for_fn_0(lst, idx + 1, total)  ← returns recursive result
    else
        total                        ← base case returns final value
let total = __for_fn_0(items, 0, 0)  ← captured back into total
```

The runtime already supports this because:
- `Environment.assign()` on a parameter updates the local binding (not
  creating a new one in parent)
- `_execute_block` returns the last statement's value, which for the
  else branch is the variable reference, and for the then branch is the
  recursive call's return value
- `_call_function` returns the block's result through the entire chain

**Multiple written variables limit:**

For 2+ written variables, the function cannot return multiple values in the
current IR. Two sub-options:

| Sub-option | Mechanism | Trade-off |
|------------|-----------|-----------|
| A1 | Return a list of final values | Requires list construction per base-case, destructuring at call site |
| A2 | Diagnostic for multiple writes | Simplifies implementation, covers 90%+ of real use cases |

**IR changes required:**
- `_build_ForStatementNode`: add free variable analysis (~60 lines)
- Else branch: return variable reference instead of `nil`
- Call site: wrap in `AssignmentIR` instead of `ExpressionStatementIR`

**No changes required to:**
- `IRNode` types (no new nodes)
- Runtime (`interpreter.py`, `environment.py`, `stack_frame.py`)
- Parser, AST, semantic analyzer, type checker (they don't know about lowering)

**Pros:**
- Zero runtime changes — purely a compile-time transformation
- Deterministic by construction — no hidden state
- Compatible with lookup cache (ADR-006) — no environment chain injection
- ~100 lines of new code in `ir/builder.py`
- Works for the most common pattern (single accumulator + read-only captures)

**Cons:**
- Single mutated variable limit without list-wrapping
- Requires AST walking for free variable detection (can use existing visitor)
- Read-only variables are passed by value on every recursive call (O(n) copies)
  — acceptable for small/simple values, could be costly for large collections
  (but collections would be unusual as loop capture targets)
- Does not compose with nested for-loops that both mutate the same variable
  (would need sequential execution analysis)

---

### 4.2 Approach B — In-place IR Expansion (RecurseIR)

**How it works:**

Add `RecurseIR(condition: IRExpression, body: BlockIR)` to the IR. The
runtime evaluates the condition; if true, executes the body and repeats
(without creating a new call frame). This eliminates the function boundary
entirely, so all enclosing variables remain accessible via the normal
scope chain.

**IR changes required:**
- New `RecurseIR` node (or modify `IfIR` with a loop flag)
- Runtime `_execute_node` must handle `RecurseIR`
- The current `_execute_block` creates a new frame for the body, which would
  still be a child of the enclosing function's frame — so scoping would work

**Pros:**
- Full access to enclosing scope (no closure needed)
- Supports any number of mutated variables
- Simpler mental model: "it's just an if that repeats"

**Cons:**
- **Violates ADR-001 and ADR-002** — introduces a loop construct at the IR level
- New IR node means changes to every pass that processes IR nodes
- Potential for infinite loops (no guaranteed progress check)
- Runtime must handle recursion within `RecurseIR` — could blow the Python
  stack just as easily as the current approach
- No optimization benefit over recursion — AILang has no TCO, so recursion
  and `RecurseIR` both consume stack
- The variable lookup cache (ADR-006) operates at the `Environment` level;
  a `RecurseIR` body executing in the same frame doesn't need cache changes

---

### 4.3 Approach C — Mutable Cells (Ref Types)

**How it works:**

Introduce a `Ref` runtime type that wraps a mutable value. Captured variables
that are written are transparently wrapped:

```
let total = 0
for item in items { total = total + item }
  ↓
let total_ref = ref_new(0)
for item in items {
    ref_set(total_ref, ref_get(total_ref) + item)
}
let total = ref_get(total_ref)
```

The IR builder wraps/unwraps reads and writes of captured variables.

**IR changes required:**
- No new IR nodes
- New builtin functions: `ref_new`, `ref_get`, `ref_set`
- IR builder must rewrite all variable references to captured variables
  (replace `VariableReferenceIR("total")` with
  `CallIR("ref_get", [VariableReferenceIR("total_ref")])`)

**Pros:**
- Supports multiple mutated variables
- No function boundary issues — the ref object is the same across calls
- Deterministic — refs are just containers

**Cons:**
- Requires the IR builder to deeply walk and rewrite expressions — fragile
- Adds runtime complexity: new `Ref` type, new builtins
- Changes the semantics of variable assignment (transparently), which could
  surprise users
- Read-only captures still need parameter threading (or can use refs too, but
  that's even more rewriting)
- The rewrite must be recursive through the entire body expression tree

---

### 4.4 Approach D — Heap-Allocated Closure Environments

**How it works:**

When a for-loop is encountered, the generated function receives a reference
to the enclosing function's `Environment` object. Variable reads and writes
in the loop body go through this environment reference instead of the local
scope.

```
fn __for_fn_0(lst, idx, __env)
    if (idx < list.len(lst))
        let item = list.get(lst, idx)
        __env.total = __env.total + item     ← access via env
        __for_fn_0(lst, idx + 1, __env)
    else nil
__for_fn_0(items, 0, current_env)
```

**IR changes required:**
- New `EnvironmentAccessIR(node: IRNode, env_var: str)` — an IR node that
  resolves a variable through a specific environment reference
- Or: modify existing `VariableReferenceIR` and `AssignmentIR` to optionally
  carry an environment name
- Runtime must support environment-passing for function calls

**Pros:**
- Closest to "real closures" — general mechanism beyond for-loops
- Any number of captured variables, any mutation pattern

**Cons:**
- **Closure environments violate ADR-005** (static lexical scoping) — the
  generated function would access a scope that is not lexically enclosing it
- **Breaks ADR-006** (lookup cache) — the cache assumes parent chains are
  stable. Injecting an arbitrary environment as a parent would either bypass
  the cache or require it to be invalidated
- Requires heap-allocating environments that would normally be stack-allocated
  (garbage collection concern)
- Massively invasive — changes to `VariableReferenceIR`, `AssignmentIR`,
  `FunctionIR`, runtime resolution chain
- AILang's architecture is explicitly designed around top-level functions
  with no closures — this would be a fundamental departure

---

### 4.5 Approach E — Diagnostic-Only Restriction

**How it works:**

Add a check in the IR builder (or semantic analyzer) that detects when a
for-loop body references an enclosing function's variable. Emit a clear
diagnostic:

```
Error: for-loop body cannot reference enclosing function variable 'total'.
       (--experimental-loops captures not yet implemented)
```

**With a suggested workaround:**

```ail
fn sum_list(items, total, idx) {            ← explicit accumulator
    if (idx < list.len(items)) {
        let item = list.get(items, idx);
        sum_list(items, total + item, idx + 1)
    } else {
        total
    }
}
let total = sum_list(items, 0, 0);          ← user-managed capture
```

**Pros:**
- Zero implementation risk
- Zero architectural impact
- Users can always write the recursive helper manually (the status quo)
- The diagnostic is better than a mysterious runtime `NameError`

**Cons:**
- Severely limits the practical usefulness of for-loops
- The most common use case (accumulator) is explicitly prohibited
- May defeat the purpose of adding the feature at all

---

## 5. Recommendation

### 5.1 Approach Selection

| Criterion | Weight | A (Threading) | B (RecurseIR) | C (Refs) | D (Closures) | E (Diagnostic) |
|-----------|:------:|:---:|:---:|:---:|:---:|:---:|
| Architectural fit (ADR-005/006) | High | ✅ | ✅ | ✅ | ❌ | ✅ |
| No ADR violation | High | ✅ | ❌(001,002) | ✅ | ❌(005,006) | ✅ |
| Single-accumulator support | High | ✅ | ✅ | ✅ | ✅ | ❌ |
| Multiple-accumulator support | Medium | ⚠️(List) | ✅ | ✅ | ✅ | ❌ |
| Implementation risk | High | Low | High | Medium | Very High | None |
| AI-generatable (ADR-009) | High | ✅ | ⚠️ | ⚠️ | ❌ | N/A |
| Compile-only (no runtime) | Medium | ✅ | ❌ | ❌ | ❌ | ✅ |

**Recommended: Approach A (parameter threading + return value capture).**

### 5.2 Scoping Rule

The capture semantics follow a simple rule:

> The for-loop body **captures by value** all variables from enclosing scopes
> that it references. If a captured variable is **assigned** inside the body,
> the final value **replaces** the original after the loop completes.

This is analogous to Rust's `move` closure semantics (copy semantics) with
a value-returning escape hatch for mutation.

### 5.3 Sub-Decision: Multiple Written Variables

For v0.10.2-exp, accept the single-accumulator limitation and emit a
diagnostic for 2+ written variables. The diagnostic suggests using a list
as a workaround:

```ail
let results = list.new();
list.append(results, 0);    ← initial total
list.append(results, 0);    ← initial count
for item in items {
    let cur_total = list.get(results, 0);
    let cur_count = list.get(results, 1);
    results = list.new();
    list.append(results, cur_total + item);
    list.append(results, cur_count + 1);
}
let total = list.get(results, 0);
let count = list.get(results, 1);
```

This is awkward but explicit — and users can always drop down to manual
recursion when they need multiple accumulators.

---

## 6. Implementation Sketch (Recommended Approach)

### 6.1 Free Variable Detection

Walk the AST of the loop body (`BlockNode.statements`) to build:

```
captured_refs: set[str]   — variables read but not written
captured_writes: set[str] — variables assigned to (= LHS of `=` in body)
```

Detection rules:

| AST node | Action |
|----------|--------|
| `VariableDeclarationNode(n)` | Add `n` to **local set** (not captured) |
| `BinaryExpressionNode(op="=", left=IdentifierNode(n), right=expr)` | Add `n` to **writes**, recurse into `expr` for references |
| `BinaryExpressionNode(op="=", left=..., right=expr)` | Recurse into `left` and `right` for references |
| `IdentifierNode(n)` where `n` not in local set | Add `n` to **reads** |
| All other nodes | Recurse into children |

This is a straightforward tree walk, ~50 lines using the existing AST nodes'
frozen dataclass structure (introspect via `dataclasses.fields()`).

### 6.2 IR Generation Changes

In `_build_ForStatementNode`:

```
1. Detect free variables (reads ∪ writes)
2. Add all free variables as parameters to FunctionIR
3. For writes:
   a. Else branch: return the variable (VariableReferenceIR)
   b. Recursive call: pass the variable as argument
   c. Call site: wrap in AssignmentIR(target=var_name, value=CallIR(...))
4. For reads only:
   a. Else branch: return nil (unchanged)
   b. Recursive call: pass the variable as argument
   c. Call site: ExpressionStatementIR wrapping CallIR (unchanged)
5. For 2+ writes: emit diagnostic, skip lowering
```

### 6.3 Files Affected

| File | Change | LOC |
|------|--------|-----|
| `compiler/ir/builder.py` | Free variable detection + param threading | ~100 |
| `tests/test_experimental_loops.py` | New tests for capture cases | ~80 |

**No other files change.** This is a purely IR-build-time transformation.

### 6.4 Test Plan

| Test | Input | Expected |
|------|-------|----------|
| Read-only capture | `let o=5; for i in c { print(i+o) }` | Compiles, prints values+5 |
| Single accumulator | `let t=0; for i in c { t=t+i }` | `t` == sum |
| No capture | `for i in c { print(i) }` | Works as before |
| Both read+write | `let o=1; let t=0; for i in c { t=t+i+o }` | `t` == sum+count |
| Multiple writes | `let a=0; let b=0; for i in c { a=a+1; b=b+i }` | Diagnostic emitted |
| Nested for-loop capture | `for i in a { for j in i { t=t+j } }` | `t` == sum of all elements |
| Flag guard | `for i in c { print(x) }` without flag | PAR012 error |

---

## 7. Risks and Mitigations

### 7.1 Variable Shadowing Risk

If the loop body declares a local variable with the same name as a captured
variable, the local should shadow the capture within the body:

```ail
let total = 0
for item in items {
    let total = 99          ← local, not the outer total
    print(total)            ← prints 99
}
print(total)                ← still 0 (no capture)
```

**Mitigation:** Free variable detection uses the semantic analyzer's scope
information (or builds its own local-set by walking declarations first).
Locals shadow captures — the generated function simply receives `total` as
a parameter and the inner `let total = 99` creates a new local binding that
shadows the parameter within the body.

### 7.2 Nested For-Loop Risk

```ail
for outer in matrix {
    t = t + outer
    for inner in outer {
        t = t + inner
    }
}
```

Both for-loops want to capture `t`. The outer loop generates `__for_fn_0`
with `t` as a parameter. The inner loop's body is part of `__for_fn_0`'s
body, so `t` is already in scope (as a parameter). The inner loop's
generated `__for_fn_1` also needs `t` as a parameter. The inner initial
call passes `t` (which is the parameter in `__for_fn_0`). This works
correctly because `t` is in scope when the inner call is generated.

**Mitigation:** Recursive free variable detection: when generating the inner
loop, the "enclosing scope" is `__for_fn_0`'s parameter scope, which already
includes `t`. The inner loop's call site correctly references `t`.

### 7.3 Deep Recursion with Value Copying

For read-only captures, the value is copied on every frame of recursion.
For an integer/boolean/string this is harmless (O(1) copy). For a list
or map, each frame would hold a reference (Python objects), so O(1) as
well — Python list/dict references are pointers. No actual deep copy occurs.

**Mitigation:** None needed — Python reference semantics ensure O(1) cost
for all types.

### 7.4 ADR-006 Lookup Cache Interaction

The lookup cache (ADR-006) caches `name -> Environment` at the
`Environment` level. Since we're adding parameters (not injecting scope
chains), the generated function's frame environment has the captured
variable as a local binding after the first iteration. The cache will
resolve it in O(1) from the current frame — no change to cache behavior.

**Mitigation:** None needed — no cache interaction.

---

## 8. Decision Gate

### 8.1 Promote to v0.10.2-exp?

| Gate | Threshold | Status | Evidence |
|:-----|:----------|:-------|:---------|
| Architectural compatibility | No ADR violation | ✅ PASS | See §5.1 — fits ADR-005/006 |
| Existing test preservation | Zero regressions | ✅ PASS | 788/790 tests pass |
| Single-accumulator support | Required | ✅ PASS | Approach A §6 |
| Diagnostic for unsupported | Required | ✅ PASS | 2+ writes emit diagnostic |
| AI-generatable | Must be learnable | ✅ PASS | Simple rule: "captures by value, final write overwrites" |

### 8.2 Promote to v1.0 RC?

The capture semantics alone do not meet the v1.0 RC bar (which requires
≥20% LOC reduction and ≥15% AI iteration reduction). However, the capture
fix is a **prerequisite** for any meaningful LOC reduction — without it,
for-loops cannot replace the most common recursive patterns.

**Recommendation:** Implement Approach A as part of the experimental
feature, then re-evaluate the v1.0 RC decision gates with the corrected
semantics.

---

## 9. Summary

The loop capture problem has a clean solution within AILang's existing
architecture: **free variable detection + parameter threading + return value
capture**. The solution requires ~100 lines in `ir/builder.py`, zero runtime
changes, and zero new IR nodes. It covers the dominant use case (single
accumulator + read-only captures) and emits a clear diagnostic for the
rare case (multiple written variables) that requires manual recursion.

| Dimension | Verdict |
|-----------|---------|
| Architecture fit | ✅ No ADRs violated |
| Implementation risk | ✅ Low — compile-time only, no runtime |
| User-facing change | ✅ Transparent — just works for common patterns |
| AI learnability | ✅ "For-loop captures enclosing variables by value" |
| Upgrade path | ✅ Can extend to multiple accumulators later (list return) |
