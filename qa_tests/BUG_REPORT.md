# AILang Validation — Comprehensive Bug Report

**Date:** 2026-07-05  
**Tester:** Independent QA Engineer  
**Scope:** All 15 test areas (scoping, shadowing, blocks, recursion, params, returns, lists, maps, JSON, CSV, imports, diagnostics, runtime errors, formatter)  
**Baseline:** 519 passing tests  

---

## Summary

| Severity | Count | Key Areas |
|----------|-------|-----------|
| **High** | 2 | AST builder crashes on invalid syntax (empty return, missing initializer) |
| **Medium** | 2 | Module reference resolution, poor error message for float literals |
| **Low** | 3 | Block shadowing unimpl., Python recursion limit, silent duplicate import |
| **Total** | **7** | |

---

## BUG-001: Empty `return;` Crashes AST Builder

**Severity:** High  
**Category:** Compiler Bug / Poor Diagnostic  
**File:** `compiler/ast/builder.py:137`

### Minimal Reproducer
```ail
fn test() {
    return
}

fn main() { return 0 }
```

### Expected Behavior
AILang spec §5.2: `return` requires a value expression. The compiler should emit a clear diagnostic: "Return statement requires a value expression" or parse it and use `null`/`None`.

### Actual Behavior
```
Traceback:
  File "compiler/ast/builder.py", line 137, in _build_ReturnStatement
    assert value is not None
AssertionError
```

The compiler crashes with an `AssertionError` — no user-facing error message.

### Root Cause
`_build_ReturnStatement` in the AST builder does a bare `assert value is not None` instead of checking and raising a proper `DiagnosticError`.

### Specification Reference
LANGUAGE_SPEC.md §5.2 Return Values: "The `return` statement immediately exits the current function and returns the value of the expression to the caller." The grammar shows `return expression;` — expression is required.

### Proposed Fix
In `compiler/ast/builder.py:_build_ReturnStatement`, replace:
```python
assert value is not None
```
with:
```python
if value is None:
    raise ValueError("Return statement requires a value expression")
```

---

## BUG-002: Missing Initializer in `let` Crashes AST Builder

**Severity:** High  
**Category:** Compiler Bug / Poor Diagnostic  
**File:** `compiler/ast/builder.py:82`

### Minimal Reproducer
```ail
fn main() {
    let x = ;
    return 0
}
```

### Expected Behavior
AILang spec §4.1: "A variable must have an initializer (there is no default value)." The compiler should emit a clear diagnostic: "Variable declaration requires an initializer expression".

### Actual Behavior
```
Traceback:
  File "compiler/ast/builder.py", line 82, in _build_VariableDeclaration
    assert initializer is not None
AssertionError
```

The compiler crashes — no user-facing error message.

### Root Cause
`_build_VariableDeclaration` does `assert initializer is not None` instead of producing a proper diagnostic.

### Specification Reference
LANGUAGE_SPEC.md §4.1 Variable Declaration: `let name = expression;` — expression is required.

### Proposed Fix
In `compiler/ast/builder.py:_build_VariableDeclaration`, replace:
```python
assert initializer is not None
```
with:
```python
if initializer is None:
    raise ValueError("Variable declaration requires an initializer expression")
```

---

## BUG-003: Module Names Not Resolvable as Bare Identifiers

**Severity:** Medium  
**Category:** Runtime Bug  
**File:** `compiler/runtime/interpreter.py:270` (`_resolve_name`)

### Minimal Reproducer
```ail
import map;

fn main() {
    let m = map.new();
    let f = map.set;
    print("f:", f);
    return 0
}
```

### Expected Behavior
`map.set` should return the function reference for `set` from the `map` module. The program should print the function reference.

### Actual Behavior
```
Runtime error: Undefined variable: map
```

The runtime cannot resolve `map` as a bare variable, even though it is an imported module. However, `map.set(...)` (with call parens) works fine because the IR builder flattens it to `"map.set"` and `_resolve_name` has special handling for dotted names.

### Root Cause
`_resolve_name` only checks `self._modules` when the name contains a `.` character (line 282). For bare module names like `map`, it falls through to `raise NameError`.

### Specification Reference
LANGUAGE_SPEC.md §9.4 Module Exports: "All top-level function and variable declarations in a module are exported by default. They are accessed through qualified names." The ability to reference a module function without immediately calling it is implied.

### Proposed Fix
In `compiler/runtime/interpreter.py:_resolve_name`, after the BUILTINS check and before the `.`-in-name check, add:
```python
module_env = self._modules.get(name)
if module_env is not None:
    return module_env
```

---

## BUG-004: Float Literal Produces Cryptic "Identifier Node Missing Token"

**Severity:** Medium  
**Category:** Poor Diagnostic  
**File:** `compiler/ast/builder.py:282`

### Minimal Reproducer
```ail
fn main() {
    let x = 3.14;
    return 0
}
```

### Expected Behavior
AILang spec §2.6.1 explicitly states: "No float literals — use integer division (22 / 7) to produce float values." The compiler should emit: "Float literals are not supported. Use integer division to produce float values."

### Actual Behavior
```
Error: Identifier node missing token
```

The parser splits `3.14` into tokens `3`, `.`, `14`, and the AST builder cannot construct an identifier from the `.14` fragment, hitting `raise ValueError("Identifier node missing token")`.

### Root Cause
The lexer/parser does not recognize decimal number literals as a single token. It tokenizes `3`, `.`, `14` separately. The `.14` part becomes an IdentifierNode without a token, which the AST builder rejects.

### Specification Reference
LANGUAGE_SPEC.md §2.6.1: "Only integer literals are supported." "No float literals."

### Proposed Fix
Option A (preferred): Add a lexer-level error for number literals containing `.`:
```
Lexer recognizes digit+'.'digit+ as a single token → emits lexical error:
"Float literals are not supported (line N, col M)"
```
Option B: Add a parser-level check: when the parser sees `number '.' number`, emit:
"Float literals are not supported. Use integer division: 22 / 7"

---

## BUG-005: Block-Level Variable Shadowing Not Implemented

**Severity:** Low  
**Category:** Language Limitation  
**File:** `compiler/runtime/interpreter.py:98` (`_execute_block`)

### Minimal Reproducer
```ail
fn main() {
    let x = "outer";
    if (1 == 1) {
        let x = "inner";
        print("inside:", x);
    }
    print("outside:", x);
    return 0
}
```

### Expected Behavior
Per AILang spec §4.3: "An inner scope can shadow an outer variable by declaring a new variable with the same name." After the if-block exits, `x` should be restored to `"outer"`. Output: `inside: inner\noutside: outer`.

### Actual Behavior
```
inside: inner
outside: inner
```

The inner `let x = "inner"` permanently overwrites the outer `x`. Shadowing does not work across block boundaries.

### Root Cause
`_execute_block` does not create a new StackFrame — it iterates statements in the current frame. All `let` bindings in nested blocks go into the same frame. To implement proper block scoping, each `{ }` block should create a new scope.

### Specification Reference
LANGUAGE_SPEC.md §4.3: "Scopes are created by function bodies ({ }) and block statements ({ })." "An inner scope can shadow an outer variable by declaring a new variable with the same name."

### Proposed Fix
Create a new StackFrame for each BlockIR that is a block statement (not function body). This requires changes in `_execute_block` and potentially in how frames are created/poped. More complex fix — defer to language evolution.

---

## BUG-006: Python Recursion Limit for Deep Recursion

**Severity:** Low  
**Category:** Language Limitation  
**File:** `compiler/runtime/interpreter.py`

### Minimal Reproducer
```ail
fn count(n) {
    if (n <= 0) { return 0 }
    return 1 + count(n - 1)
}

fn main() {
    print(count(10000));
    return 0
}
```

### Expected Behavior
The AILang spec doesn't specify a recursion limit. A reasonably deep recursion should work.

### Actual Behavior
```
Runtime error: maximum recursion depth exceeded while calling a Python object
```

The limit is hit between 500-1000 recursive calls (Python's default recursion limit is 1000 and the interpreter's own overhead reduces this further).

### Root Cause
The AILang runtime uses Python call frames for recursion. Python's recursion limit (default ~1000) applies. Each AILang function call creates Python call frames for `_call_function → _execute_block → _execute_node → ...`.

### Specification Reference
No explicit recursion limit in the spec.

### Proposed Fix
No fix within the current architecture. Document the effective recursion limit (~500 calls) in the spec. For deeper recursion, users must use iterative patterns (which AILang doesn't support — no loops). This is a known constraint.

---

## BUG-007: Duplicate Import Silently Accepted

**Severity:** Low  
**Category:** Compiler Bug (Minor)  
**File:** `compiler/semantic/analyzer.py`

### Minimal Reproducer
```ail
import list;
import list;

fn main() { return 0 }
```

### Expected Behavior
Should produce a warning or error: "Duplicate import: list".

### Actual Behavior
Compiles and runs without any diagnostic.

### Specification Reference
LANGUAGE_SPEC.md §9.1: No explicit statement about duplicate imports.

### Proposed Fix
Add a check in `compiler/semantic/analyzer.py` to detect duplicate imports and emit a diagnostic (MOD003 or similar).

---

## Non-Bug Observations

| Observation | Status |
|-------------|--------|
| Negative numbers in arithmetic work correctly | ✅ |
| Mixed-type lists (int, string, bool) work | ✅ |
| Nested lists/maps work correctly | ✅ |
| `list.remove` on empty list is safe (no crash) | ✅ |
| `map.delete` on missing key is safe (no crash) | ✅ |
| `list.contains` on empty list returns False | ✅ |
| `map.has` on empty map returns False | ✅ |
| Truthiness: 0 is falsy, 1 is truthy, "" is falsy | ✅ (Python behavior) |
| `map.get` on missing key raises error | ✅ (documented behavior) |
| Formatting nested if-blocks works correctly | ✅ |
| Forward references between functions not supported | ⚠️ Known limitation |
| `_` as identifier causes "Duplicate declaration" | ⚠️ Known: `_` is treated as a re-declaration |
| `print` output format matches expected | ✅ |

---

## Test Coverage Summary

| Area | Tests Run | Bugs Found | Status |
|------|-----------|------------|--------|
| Variable scoping | 5 | 1 (BUG-005) | ⚠️ |
| Variable shadowing | 3 | 1 (BUG-005) | ⚠️ |
| Nested blocks | 3 | 1 (BUG-005) | ⚠️ |
| Deep recursion | 2 | 1 (BUG-006) | ⚠️ |
| Mutual recursion | 1 | 0 (forward ref limitation) | ⚠️ |
| Function parameters | 4 | 1 (BUG-001) | ⚠️ |
| Return values | 4 | 1 (BUG-001) | ⚠️ |
| List operations | 8 | 0 | ✅ |
| Map operations | 8 | 0 | ✅ |
| JSON serialization | 4 | 0 | ✅ |
| CSV handling | 3 | 0 | ✅ |
| Module imports | 4 | 2 (BUG-003, BUG-007) | ⚠️ |
| Error diagnostics | 5 | 2 (BUG-002, BUG-004) | ⚠️ |
| Runtime errors | 4 | 0 | ✅ |
| Formatter behavior | 4 | 0 | ✅ |
| **Total** | **62** | **7** | |

---

## Impact Analysis

### High Severity (BUG-001, BUG-002)
These cause the compiler to crash (AssertionError) instead of producing user-friendly diagnostics. This is the most impactful class of bug because it degrades the developer experience severely — any syntax error in these specific patterns crashes the tool rather than reporting the error.

### Medium Severity (BUG-003, BUG-004)
BUG-003 prevents using module functions as first-class values. Any code that tries to reference a module function without immediately calling it will fail at runtime. BUG-004 provides a cryptic error message for a common user mistake (writing float literals).

### Low Severity (BUG-005, BUG-006, BUG-007)
BUG-005 is a feature gap (block scoping is specified but not implemented). BUG-006 is a fundamental platform limitation. BUG-007 is a minor quality-of-life issue.

---

## Recommendations for v0.2.0

1. **Fix all `assert` crashes in AST builder** (BUG-001, BUG-002) — replace bare `assert` with proper diagnostic errors
2. **Add module name resolution** (BUG-003) — 3-line fix in `_resolve_name`
3. **Improve float literal error** (BUG-004) — lexer-level detection with clear message
4. **Document recursion limit** — add to LANGUAGE_SPEC.md
5. **Consider block scoping implementation** (BUG-005) — most impactful feature gap
