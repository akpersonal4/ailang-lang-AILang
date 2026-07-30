# M84R.2 — Root Cause Analysis

**Date:** 2026-07-22

---

## P0 — Module Resolution Fallback Missing for Installed Packages

### Root Cause

`ModuleResolver._candidate_roots()` in `compiler/compilation/resolution.py` builds search paths by walking up from the source file's parent directory, checking for `stdlib/` and `lib/` subdirectories at each ancestor. This works within the source repository (where `stdlib/` is a sibling directory), but fails when the project is outside the repo — e.g., after `pip install ailang-lang` and creating a project in the user's home directory.

### Affected Component

`compiler/compilation/resolution.py` — `_candidate_roots()` method

### Impact

Any AILang program that imports stdlib modules (e.g., `import math`, `import list`) fails with MOD003 when run from a non-repository directory. The default `ail new` template (which only uses `print()`) is unaffected.

### Why Previous Testing Missed It

All tests run from within the source repository where `stdlib/` is always accessible via the directory walk. No tests simulate a pip-installed user environment running from an unrelated directory.

### Fix Strategy

Add a `_bundled_stdlib_root()` helper that locates the stdlib directory shipped with the ailang-lang package (either editable or pip-installed), and append it as a fallback root in `_candidate_roots()`.

---

## P1 — list.sum Float Truncation

### Root Cause

`list_sum()` in `compiler/runtime/builtins.py` initializes the accumulator as `int(0)` and casts every item via `int(item)`. Python's `int()` truncates toward zero, silently discarding fractional parts. The same bug exists in `list_sum_by_key()`.

### Affected Component

`compiler/runtime/builtins.py` — `list_sum()` (line 60) and `list_sum_by_key()` (line 140)

### Impact

Any program using `list.sum()` or `list.sum_by_key()` with floating-point values gets silently incorrect results. This affects financial calculations, statistical aggregations, and any business application working with decimal values.

### Why Previous Testing Missed It

The existing test `test_list_sum_by_key_sums_values` uses only integer string values (`"10"`, `"20"`, `"30"`). No test cases use floating-point inputs.

### Fix Strategy

Change both functions to use a typed accumulator: track whether any item is `float`, and if so, promote the accumulator to `float`. Return `int` when all items are integers, `float` when any item is a float.

---

## P2 — Not Reproduced

The evaluator claimed `list.sort_by_key()` calls the wrong native function. In reality, both `list.sort` and `list.sort_by_key` correctly delegate to the polymorphic `list_sort` native function, which handles both plain and key-based sorting via argument count. No fix needed.

---

## Version Mismatch

### Root Cause

`pyproject.toml` and `compiler/_version.py` were updated to `1.1.1`, but the installed package metadata (from PyPI) still reflects `1.1.0`. This is a packaging metadata sync issue — the source was bumped without rebuilding the wheel.

### Impact

`pip show ailang-lang` reports a stale version. This is cosmetic but confusing for users verifying their installation.

### Fix Strategy

Ensure `pyproject.toml` and `compiler/_version.py` are in sync, and rebuild the wheel before publishing.
