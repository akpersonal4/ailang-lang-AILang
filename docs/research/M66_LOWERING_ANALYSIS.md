# M66 — Lowering Analysis

**Date:** 2026-07-14
**Status:** Complete
**Depends on:** ADR-00X (Bounded Iteration)

---

## 1. Overview

This document analyzes the compiler lowering from `for-in` loops to recursive
functions. The lowering is a compile-time transformation that produces
deterministic, transparent recursion from loop syntax.

---

## 2. Lowering Rules

### 2.1 Basic Pattern

**Input:**
```ail
for item in collection {
    body;
}
```

**Output:**
```ail
fn __for_fn_N(__lst_N, __idx_N) {
    if (__idx_N < list.len(__lst_N)) {
        let item = list.get(__lst_N, __idx_N);
        body;
        __for_fn_N(__lst_N, __idx_N + 1);
    } else {
        nil;
    }
}
__for_fn_N(collection, 0);
```

### 2.2 With Single Accumulator

**Input:**
```ail
let total = 0;
for item in items {
    total = total + item;
}
```

**Output:**
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

### 2.3 With Read-Only Capture

**Input:**
```ail
let offset = 10;
for item in items {
    print(item + offset);
}
```

**Output:**
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

---

## 3. Properties

| Property | Guarantee | Evidence |
|----------|-----------|----------|
| **Determinism** | Same AST → identical generated code | IR builder is pure function of AST |
| **No new IR nodes** | Uses existing FunctionIR, CallIR, IfIR | No interpreter changes needed |
| **No runtime changes** | Interpreter unchanged | All transformation at IR-build time |
| **No hidden state** | All state in parameters and return values | Generated code is transparent |
| **Transparent** | Developer can read the generated recursion | Lowering is documented and predictable |

---

## 4. Uniqueness Guarantees

| Counter | Scope | Purpose |
|---------|-------|---------|
| `__for_fn_N` | Per for-statement | Unique function name |
| `__lst_N` | Per for-statement | Unique list parameter |
| `__idx_N` | Per for-statement | Unique index parameter |

Multiple for-loops in the same function produce `__for_fn_0`, `__for_fn_1`, etc.

Nested for-loops produce `__for_fn_0` (outer) and `__for_fn_1` (inner), with
the inner function defined inside the outer's body.

---

## 5. Dependencies

The lowering emits calls to `list.len` and `list.get`, which require:

```ail
import list;
```

**Without this import, the lowering fails at runtime** (not at compile time,
because the generated function is not analyzed until called).

**Mitigation:** The semantic analyzer should warn when `for-in` is used
without `import list`.

---

## 6. Capture Analysis Summary

| Variable Type | Parameter | Initial Value | Return Value | Call Site |
|--------------|-----------|---------------|--------------|-----------|
| Loop variable | `item` | `list.get(lst, idx)` | N/A | N/A |
| Read-only | `var` | `var` (passed through) | N/A | `__for_fn_N(lst, 0, var)` |
| Written (accumulator) | `var` | `var` (initial value) | `var` (final value) | `let var = __for_fn_N(lst, 0, var)` |

**Single accumulator limit:** Only one variable may be written inside the loop body.
Multiple writes raise `ValueError: "Only one accumulator variable allowed"`.

---

## 7. Edge Cases

| Case | Behavior | Status |
|------|----------|:------:|
| Empty list | Body never executes, returns nil | ✅ |
| Single element | Body executes once | ✅ |
| Nested for-loops | Inner loop inside outer's body | ✅ |
| For-loop in helper function | Works (function is module-level) | ✅ |
| Read-only + write capture | Both supported together | ✅ |
| Multiple writes | ValueError raised | ✅ |
| For-loop without `import list` | Runtime error (list module not found) | ⚠️ |

---

## 8. Test Coverage

| Test | Category | Status |
|------|----------|:------:|
| `test_for_sum_list` | Basic iteration | ✅ |
| `test_for_count_items` | Counter pattern | ✅ |
| `test_for_max_element` | Conditional update | ✅ |
| `test_for_empty_list` | Edge case | ✅ |
| `test_for_single_element` | Edge case | ✅ |
| `test_for_nested` | Nested loops | ✅ |
| `test_for_in_helper_function` | Helper function | ✅ |
| `test_for_rejected_without_flag` | Flag guard | ✅ |
| `test_for_print_elements` | Side effects | ✅ |
| `test_for_read_only_capture` | Read-only capture | ✅ |
| `test_for_read_only_multiple` | Multiple read-only | ✅ |
| `test_for_mixed_read_write` | Mixed capture | ✅ |
| `test_for_capture_in_if_body` | Conditional write | ✅ |
| `test_for_capture_no_accumulator` | Read-only only | ✅ |
| `test_for_capture_flag_guard` | Flag pattern | ✅ |
| `test_for_multiple_writes_rejected` | Error case | ✅ |

**Total: 16 tests, all passing**

---

## 9. Conclusion

The lowering from for-in to recursion is:

1. **Deterministic** — same AST produces identical generated code
2. **Transparent** — the generated recursion is readable
3. **Complete** — all 8 formal rules are enforced
4. **Tested** — 16 test cases covering basic, edge, and capture scenarios
5. **Safe** — no new IR nodes, no runtime changes, no hidden state

The lowering satisfies all requirements for bounded deterministic iteration.
