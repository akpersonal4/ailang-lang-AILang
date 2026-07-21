# M66 — Capture Analysis

**Date:** 2026-07-14
**Status:** Complete
**Depends on:** ADR-00X (Bounded Iteration), M26 (Loop Capture Semantics)

---

## 1. Overview

This document analyzes the variable capture semantics for `for-in` loops in
AILang. The capture mechanism allows loop bodies to access and modify variables
from enclosing function scopes while preserving AILang's architectural
constraints (no closures, static lexical scoping).

---

## 2. Problem

The for-in loop lowers to a **module-level recursive helper function**. Because
AILang uses static lexical scoping (ADR-005) and does not support closures, the
generated function cannot access variables from the enclosing function's scope.

```ail
fn main() {
    let total = 0;
    for item in items {
        total = total + item;  ❌ 'total' not in scope of __for_fn_0
    }
    return total;
}
```

The runtime scope chain for `__for_fn_0` is:
```
__for_fn_0 frame → global environment
```

But `total` lives in:
```
main frame → global environment
```

These are sibling chains, not parent-child.

---

## 3. Solution: Parameter Threading

### 3.1 Mechanism

1. **Detect** free variables in the loop body (variables not declared locally)
2. **Categorize** as read-only or written (appears on LHS of `=`)
3. **Add parameters** to the generated function for each free variable
4. **Thread through** recursive calls
5. **Capture at call site** for written variables

### 3.2 Read-Only Capture

```ail
let offset = 10;
for item in items {
    print(item + offset);
}
```

↓

```ail
fn __for_fn_N(__lst_N, __idx_N, offset) {
    if (__idx_N < list.len(__lst_N)) {
        let item = list.get(__lst_N, __idx_N);
        print(item + offset);
        __for_fn_N(__lst_N, __idx_N + 1, offset);
    } else {
        nil;
    }
}
__for_fn_N(items, 0, offset);
```

**Property:** `offset` is passed by value on every recursive call. For
primitives (int, string, bool), this is O(1). For collections (list, map),
Python reference semantics ensure O(1) as well.

### 3.3 Written (Accumulator) Capture

```ail
let total = 0;
for item in items {
    total = total + item;
}
```

↓

```ail
fn __for_fn_N(__lst_N, __idx_N, total) {
    if (__idx_N < list.len(__lst_N)) {
        let item = list.get(__lst_N, __idx_N);
        total = total + item;
        __for_fn_N(__lst_N, __idx_N + 1, total);
    } else {
        total;
    }
}
let total = __for_fn_N(items, 0, 0);
```

**Property:** The base case returns `total`. The recursive call passes the
updated `total`. The call site captures the return value back into `total`.

---

## 4. Variable Categories

| Category | Example | Detection | Mechanism |
|----------|---------|-----------|-----------|
| Loop variable | `item` in `for item in ...` | Declared in lowering | `let item = list.get(...)` |
| Module-level var | `list` in `list.len(...)` | Resolves via global | No capture needed |
| Read-only capture | `offset` in `print(item + offset)` | Referenced but not assigned | Parameter threading |
| Written capture | `total` in `total = total + item` | Assigned in body | Parameter + return value |

---

## 5. Detection Algorithm

### 5.1 AST Walk

```
function detect_free_variables(body, local_names):
    reads = set()
    writes = set()
    
    for each node in body:
        if node is VariableDeclarationNode(name):
            local_names.add(name)
        
        else if node is AssignmentNode(target, value):
            if target is IdentifierNode(name) and name not in local_names:
                writes.add(name)
            walk(value, local_names, reads, writes)
        
        else if node is IdentifierNode(name):
            if name not in local_names:
                reads.add(name)
        
        else:
            walk children recursively
    
    return reads, writes
```

### 5.2 Categorization

| Reads | Writes | Result |
|-------|--------|--------|
| Empty | Empty | No capture needed |
| Non-empty | Empty | Read-only parameters |
| Empty | Non-empty | Not possible (write implies read) |
| Non-empty | Non-empty | Mixed capture (read params + write return) |

---

## 6. Restrictions

### 6.1 Single Accumulator Limit

**Only one variable may be written** inside the loop body.

**Reason:** The generated function can only return one value. Multiple written
variables would require returning a list and destructuring at the call site,
which adds complexity and reduces transparency.

**Error:** `ValueError: "Only one accumulator variable allowed in for-loop body"`

**Workaround:** Use manual recursion for multiple accumulators.

### 6.2 No Nested For-Loop Mutation of Same Variable

```ail
for outer in matrix {
    t = t + outer;
    for inner in outer {
        t = t + inner;  ❌ Nested for-loops cannot both mutate 'total'
    }
}
```

**Reason:** The inner loop's generated function would need to capture `t` from
the outer loop's generated function, which is a different scope. The parameter
threading mechanism works for the outer loop, but the inner loop's capture of
the same variable creates ambiguity about which return value to use.

**Workaround:** Use manual recursion for nested mutation patterns.

---

## 7. ADR Compliance

| ADR | Status | Evidence |
|-----|:------:|----------|
| ADR-001 (Recursion-only) | ✅ | Lowering produces recursion |
| ADR-002 (No loop constructs) | ✅ | For-in is syntax sugar, not a loop construct |
| ADR-005 (Static lexical scoping) | ✅ | No scope chain injection |
| ADR-006 (Lookup cache) | ✅ | Parameters are local bindings, cache works normally |
| ADR-007 (Evidence-first) | ✅ | M65A provides evidence base |
| ADR-009 (AI-first) | ✅ | Simple rule: "captures by value" |

---

## 8. Test Coverage

| Test | Scenario | Status |
|------|----------|:------:|
| `test_for_read_only_capture` | Single read-only variable | ✅ |
| `test_for_read_only_multiple` | Multiple read-only variables | ✅ |
| `test_for_mixed_read_write` | Read-only + write together | ✅ |
| `test_for_capture_in_if_body` | Write inside conditional | ✅ |
| `test_for_capture_no_accumulator` | Read-only only, no write | ✅ |
| `test_for_capture_flag_guard` | Flag variable capture | ✅ |
| `test_for_multiple_writes_rejected` | Error case | ✅ |

**Total: 7 capture tests, all passing**

---

## 9. Performance Characteristics

| Operation | Cost | Notes |
|-----------|------|-------|
| Read-only capture | O(1) per call | Value copy (primitives) or reference copy (collections) |
| Write capture | O(1) per call | Parameter + return value |
| Free variable detection | O(n) | One-time AST walk at IR-build time |
| No runtime overhead | O(0) | All transformation at compile time |

---

## 10. Conclusion

The capture semantics for for-in loops:

1. **Preserve AILang's architecture** — no closures, no scope injection
2. **Cover common patterns** — single accumulator + read-only captures
3. **Emit clear errors** — multiple writes raise ValueError
4. **Are deterministic** — same AST produces same parameter threading
5. **Are transparent** — generated code is readable

The capture mechanism is a compile-time transformation that works within
AILang's existing constraints.
