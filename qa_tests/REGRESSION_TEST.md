# AILang Regression Tests — Validation Report

These tests should be added to the existing test suite (alongside the 519 passing tests) to prevent re-introduction of the 7 discovered bugs.

---

## Test Structure

Each test follows this pattern:
```ail
// REGRESSION-00X: <bug-title>
// Expected: <expected-output-or-error>
```

---

## REGRESSION-001: Empty return should produce diagnostic, not crash

**Status:** ❌ Fails (crashes with AssertionError)  
**Test file:** `qa_tests/regression_001_empty_return.ail`

```ail
fn test() { return }
fn main() { return 0 }
```

**Expected:** Compiler produces: "Return statement requires a value expression"  
**Actual:** `AssertionError` crash  
**Bug ref:** BUG-001

---

## REGRESSION-002: Missing initializer should produce diagnostic, not crash

**Status:** ❌ Fails (crashes with AssertionError)  
**Test file:** `qa_tests/regression_002_missing_init.ail`

```ail
fn main() {
    let x = ;
    return 0
}
```

**Expected:** Compiler produces: "Variable declaration requires an initializer expression"  
**Actual:** `AssertionError` crash  
**Bug ref:** BUG-002

---

## REGRESSION-003: Module function as first-class value

**Status:** ❌ Fails (runtime error at `map.set`)  
**Test file:** `qa_tests/regression_003_module_ref.ail`

```ail
import map;
fn main() {
    let m = map.new();
    let f = map.set;
    return 0
}
```

**Expected:** Program runs successfully (stores function reference in `f`)  
**Actual:** "Runtime error: Undefined variable: map"  
**Bug ref:** BUG-003

---

## REGRESSION-004: Float literal should produce clear error

**Status:** ❌ Fails (cryptic error)  
**Test file:** `qa_tests/regression_004_float_literal.ail`

```ail
fn main() {
    let x = 3.14;
    return 0
}
```

**Expected:** Compiler produces: "Float literals are not supported"  
**Actual:** "Identifier node missing token"  
**Bug ref:** BUG-004

---

## REGRESSION-005: Block variable shadowing

**Status:** ❌ Fails (no shadowing)  
**Test file:** `qa_tests/regression_005_block_shadow.ail`

```ail
fn main() {
    let x = "outer";
    if (1 == 1) {
        let x = "inner";
    }
    print(x);
    return 0
}
```

**Expected:** Output: `outer`  
**Actual:** Output: `inner`  
**Bug ref:** BUG-005

---

## REGRESSION-006: Deep recursion handled gracefully

**Status:** ⚠️ Known limitation  
**Test file:** `qa_tests/regression_006_deep_recursion.ail`

```ail
fn count(n) {
    if (n <= 0) { return 0 }
    return 1 + count(n - 1)
}
fn main() { print(count(10000)); return 0 }
```

**Expected:** Output: `0` (computed via tail recursion or iterative evaluation)  
**Actual:** "maximum recursion depth exceeded" at ~500 calls  
**Bug ref:** BUG-006  
**Note:** Language limitation, not a defect per se. Document limit and accept.

---

## REGRESSION-007: Duplicate import produces warning

**Status:** ❌ Fails (no warning)  
**Test file:** `qa_tests/regression_007_dup_import.ail`

```ail
import list;
import list;
fn main() { return 0 }
```

**Expected:** Compiler warning: "Duplicate import: list"  
**Actual:** No diagnostic  
**Bug ref:** BUG-007

---

## Regression Test Runner (Pseudo-Code)

```python
# To be integrated into the existing test harness

regression_tests = [
    ("regression_001_empty_return",  "build", None,           True),     # expect compile error
    ("regression_002_missing_init",  "build", None,           True),     # expect compile error
    ("regression_003_module_ref",    "run",   None,           True),     # should eventually pass
    ("regression_004_float_literal", "build", None,           True),     # expect compile error
    ("regression_005_block_shadow",  "run",   "outer\n",      False),    # should output "outer"
    ("regression_006_deep_recursion","run",   "0\n",          False),    # should output "0"
    ("regression_007_dup_import",    "build", None,           True),     # expect warning
]

for name, mode, expected_output, expect_error in regression_tests:
    result = run_test(f"qa_tests/{name}.ail", mode)
    assert result.exit_code == (1 if expect_error else 0), f"{name}: expected {'error' if expect_error else 'success'}"
    if expected_output:
        assert result.stdout == expected_output, f"{name}: expected {expected_output!r}, got {result.stdout!r}"
```

---

## Current Status

All 7 regression tests fail. Once the corresponding bugs are fixed, these tests should pass. Adopt the following priority order:

1. REGRESSION-001, REGRESSION-002 (High — crash bugs)
2. REGRESSION-003, REGRESSION-004 (Medium — feature gap / poor diagnostics)
3. REGRESSION-005, REGRESSION-006, REGRESSION-007 (Low — feature gap / minor issues)
