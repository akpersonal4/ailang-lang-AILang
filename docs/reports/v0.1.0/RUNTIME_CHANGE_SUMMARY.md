# Runtime Change Summary — Compiler QA Bug Fix Sprint #001

**Scope**: 6 bug fixes across 5 files
**Test impact**: 522 tests pass (up from 519), 3 new regression tests
**Total lines changed**: ~50 lines

---

## Files Modified

### 1. `compiler/ast/builder.py` (2 changes, +4 lines)

**BUG-001** (line 82): `_build_ReturnStatement`
```python
# Before
assert False, "Return statement requires an expression"

# After
raise ValueError("Return statement requires an expression")
```

**BUG-002** (line 137): `_build_VariableDeclaration`
```python
# Before
assert False, "Variable declaration requires an initializer expression"

# After
raise ValueError("Variable declaration requires an initializer expression")
```

### 2. `compiler/lexer.py` (1 change, +9 lines)

**BUG-004** (lines 208-216): Float literal detection
```python
# After emitting number token, check for .digits
pos = self._pos
while pos < len(self._text) and self._text[pos].isdigit():
    pos += 1
if pos < len(self._text) and self._text[pos] == ".":
    end = pos + 1
    while end < len(self._text) and self._text[end].isdigit():
        end += 1
    if end > pos + 1:
        raise ValueError(
            "Float literals are not supported. Use integer division, e.g. 22 / 7"
        )
```

### 3. `compiler/diagnostics.py` (1 change, +1 line)

**BUG-004** (new error code):
```python
LEX004_FLOAT_LITERAL = ErrorCode("LEX004", "Float literal")
```

### 4. `compiler/runtime/interpreter.py` (4 changes, +15 lines)

**BUG-003** (line 266): Module function registration in `_execute_node_in_module`
```python
module_env.define(node.name, node)  # register in module env
```

**BUG-003** (lines 283-285): Module name lookup in `_resolve_name`
```python
module_env = self._modules.get(name)
if module_env is not None:
    return module_env
```

**BUG-005** (lines 98-107): Block scoping in `_execute_block`
```python
# Before
def _execute_block(self, block: BlockIR) -> Any:
    result: Any = None
    for statement in block.statements:
        result = self._execute_node(statement)
        if isinstance(statement, ReturnIR) or isinstance(result, ReturnSignal):
            return result
    return result

# After
def _execute_block(self, block: BlockIR) -> Any:
    frame = StackFrame(
        parent_frame=self._frame_stack[-1] if self._frame_stack else None,
    )
    self._frame_stack.append(frame)
    try:
        result: Any = None
        for statement in block.statements:
            result = self._execute_node(statement)
            if isinstance(statement, ReturnIR) or isinstance(result, ReturnSignal):
                return result
        return result
    finally:
        self._frame_stack.pop()
```

**BUG-006** (lines 3, 40): Recursion limit increase
```python
import sys  # line 3

class Runtime:
    def __init__(self, module_bundle=None):
        sys.setrecursionlimit(10000)  # line 40
```

### 5. `CHANGELOG.md` (1 change, +4 lines)

Updated entries for BUG-005, BUG-006, updated test count to 522.

### 6. Test files (3 new tests, +26 lines)

| Test file | New tests |
|---|---|
| `tests/test_ast_builder.py` | `test_ast_rejects_empty_return`, `test_ast_rejects_missing_initializer` |
| `tests/test_lexer.py` | `test_lexer_rejects_float_literal` |
| `tests/test_validation.py` | `test_regression_module_function_as_value` (replaced no-op `test_limitation_module_function_calls`) |

---

## Runtime Architecture Impact

### Frame Stack Lifecycle (before vs after BUG-005)

**Before** (incorrect scoping):
```
_call_function → push StackFrame(function)
  _execute_block → no new frame (variables leak)
    _execute_block (if/else) → no new frame (variables leak)
  ← pop StackFrame(function)
```

**After** (correct scoping):
```
_call_function → push StackFrame(function)
  _execute_block → push StackFrame(block)
    _execute_block (if/else) → push StackFrame(block)
    ← pop StackFrame(block)
  ← pop StackFrame(block)
← pop StackFrame(function)
```

### Module Name Resolution (before vs after BUG-003)

**Before**: `_resolve_name` checked frames → globals → builtins → `"." in name` branch. Bare module names like `map` would not match any of these and raise `NameError`.

**After**: Added `self._modules.get(name)` check between builtins and dot-name branch. A bare `"map"` now finds the module environment.

---

## Risk Assessment

| Change | Risk Level | Mitigation |
|---|---|---|
| BUG-001 (ValueError) | Minimal | Same error path, just better message |
| BUG-002 (ValueError) | Minimal | Same error path, just better message |
| BUG-003 (module resolution) | Low | Only adds new resolution path, never breaks existing |
| BUG-004 (float literal) | Minimal | Only affects `.digit` sequences, `ident.digit` still works |
| BUG-005 (block scoping) | Medium | Changes variable scoping semantics; verified via 18 runtime tests + 522 full suite |
| BUG-006 (recursion limit) | Minimal | Only increases capacity, no semantic change |

## Verification Summary

- **522/522 pytest tests pass** (100%)
- **25/25 benchmark tests pass** (100%)
- **34/34 expected-to-pass qa_tests pass** (100%)
- **14 expected-to-fail qa_tests** produce correct error diagnostics
- **0 regressions** detected
- **All changes** verified against LANGUAGE_SPEC.md
