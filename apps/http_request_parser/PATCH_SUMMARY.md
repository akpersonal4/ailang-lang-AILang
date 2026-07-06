# Patch Summary: RUNTIME-001

## File Changed

`compiler/runtime/interpreter.py`

## Change Description

Split the `_set_local` method into two distinct methods — one for `let` variable
declarations and one for `=` reassignments — so that `let` always creates a
local variable in the current scope.

## Before (buggy)

```python
def _set_local(self, name: str, value: Any) -> None:
    if self._frame_stack:
        self._frame_stack[-1].assign(name, value)
    else:
        self._global_environment.define(name, value)
```

Used for **both** `VariableDeclarationIR` and `AssignmentIR`:

```python
if isinstance(node, VariableDeclarationIR):
    value = self._evaluate_expression(node.initializer)
    self._set_local(node.name, value)          # should be define()
    return value
if isinstance(node, AssignmentIR):
    value = self._evaluate_expression(node.value)
    self._set_local(node.target, value)         # should be assign()
    return value
```

## After (fixed)

```python
def _define_local(self, name: str, value: Any) -> None:
    """For 'let' declarations: always create a local variable."""
    if self._frame_stack:
        self._frame_stack[-1].define(name, value)
    else:
        self._global_environment.define(name, value)

def _assign_local(self, name: str, value: Any) -> None:
    """For '=' reassignments: search scope chain and update."""
    if self._frame_stack:
        self._frame_stack[-1].assign(name, value)
    else:
        self._global_environment.define(name, value)
```

Update the handlers:

```python
if isinstance(node, VariableDeclarationIR):
    value = self._evaluate_expression(node.initializer)
    self._define_local(node.name, value)        # FIXED: was _set_local
    return value
if isinstance(node, AssignmentIR):
    value = self._evaluate_expression(node.value)
    self._assign_local(node.target, value)       # FIXED: was _set_local
    return value
```

## Diff Summary

```
4 lines added (new methods _define_local, _assign_local)
3 lines removed (old _set_local)
1 line modified (VariableDeclarationIR calls _define_local)
1 line modified (AssignmentIR calls _assign_local)
```

## Files Added

- `tests/test_runtime.py` — 7 new regression tests:
  - `test_runtime_cross_function_isolation`
  - `test_runtime_same_name_three_functions`
  - `test_runtime_recursive_let_isolation`
  - `test_runtime_repeated_call_returns_same_value`
  - `test_runtime_independent_scope_chains`
  - `test_runtime_assignment_uses_correct_scope`
  - `test_runtime_assignment_finds_outer_variable`

## Verification

- 519 tests pass (512 existing + 7 new)
- `apps/http_request_parser/main.ail` runs correctly (all 4 samples)
- No regressions detected
