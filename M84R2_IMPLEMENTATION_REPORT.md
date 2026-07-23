# M84R.2 — Implementation Report

**Date:** 2026-07-22

---

## Fix 1: Module Resolution Fallback for Bundled Stdlib

### File Changed

`compiler/compilation/resolution.py`

### Changes

1. Added `_bundled_stdlib_root()` function that locates the stdlib directory shipped with the ailang-lang package:
   - In an editable install: `<repo>/stdlib/` (sibling to `compiler/`)
   - In a pip wheel install: `<site-packages>/stdlib/` (sibling to `compiler/`)

2. Modified `_candidate_roots()` to append the bundled stdlib path as the final fallback after all directory-walk candidates.

### Code

```python
def _bundled_stdlib_root() -> Path | None:
    """Locate the stdlib directory shipped with the ailang-lang package."""
    import compiler as _pkg
    pkg_dir = Path(_pkg.__file__).resolve().parent
    candidate = pkg_dir.parent / "stdlib"
    if candidate.is_dir():
        return candidate
    return None
```

### Verification

```bash
# From a non-repo directory:
import math;
let x = math.add(10, 20);
io.writeln(convert.to_string(x))
# Before fix: ERROR MOD003: Module not found: math
# After fix: 30
```

---

## Fix 2: list.sum Float Handling

### File Changed

`compiler/runtime/builtins.py`

### Changes

1. `list_sum()`: Changed accumulator from `int` to `int | float`. When a `float` item is encountered, the accumulator is promoted to `float`. Integer-only lists still return `int`.

2. `list_sum_by_key()`: Same fix applied.

### Code

```python
def list_sum(args: tuple[RuntimeValue, ...]) -> int | float:
    total: int | float = 0
    for item in args[0]:
        if isinstance(item, float):
            if not isinstance(total, float):
                total = float(total)
            total += item
        else:
            total += int(item)
    return total
```

### Verification

```bash
# Float values: 15.5 + 2.5 + 4.0
# Before fix: 21 (truncated)
# After fix:  22.0 (correct)

# Integer values: 10 + 20 + 30
# Before fix: 60
# After fix:  60 (unchanged)

# Mixed values: 10 + 2.5 + 30
# Before fix: 40 (truncated)
# After fix:  42.5 (correct)
```

---

## Files Modified

| File | Lines Changed | Description |
|------|:------------:|-------------|
| `compiler/compilation/resolution.py` | +18 | Added `_bundled_stdlib_root()` and fallback in `_candidate_roots()` |
| `compiler/runtime/builtins.py` | +18 | Fixed `list_sum()` and `list_sum_by_key()` float handling |

**Total: 2 files, ~36 lines added, 10 lines modified**
