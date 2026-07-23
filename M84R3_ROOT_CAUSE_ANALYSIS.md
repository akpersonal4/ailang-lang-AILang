# M84R.3 — Root Cause Analysis

**Date:** 2026-07-22
**Version:** v1.1.2

---

## P0 — Standard Library Module Resolution (MOD003)

### Root Cause

The `_try_discover_stdlib_via_package()` method in `compiler/compilation/session.py` uses `importlib.metadata` to locate the stdlib directory from the installed wheel's RECORD file. The RECORD file contains **relative paths** (e.g., `stdlib/math.ail`), but the code created a `_Path(parts[0])` which is a relative path resolved against the **current working directory** — not the distribution's installation location.

When a user runs `ail run main.ail` from their home directory (e.g., `C:\Users\user\demo\`), the relative path `stdlib/math.ail` resolves to `C:\Users\user\demo\stdlib\math.ail`, which does not exist. The upward directory walk also fails because the user's project directory has no `stdlib/` subdirectory.

### Exact Defect Location

**File:** `compiler/compilation/session.py`, line 220

**Before (broken):**
```python
entry_path = _Path(parts[0])  # Relative path! Resolved against CWD
```

**After (fixed):**
```python
entry_path = dist.locate_file(parts[0])  # Resolves against dist location
```

### Affected Files

| File | Change |
|------|--------|
| `compiler/compilation/session.py` | Line 220: `_Path(parts[0])` → `dist.locate_file(parts[0])` |

### Why Previous Validation Missed It

1. **All tests run from within the source repository** where `stdlib/` is always found via the upward directory walk (line 133-150 in session.py). The importlib.metadata fallback was never exercised in a real test.
2. **No test simulates a pip-installed user environment** running from an unrelated directory.
3. **The `test_stdlib_discovery.py` tests** mock `Path.cwd()` but never test the actual importlib.metadata RECORD parsing with relative paths.

### Why Regression Tests Passed

- The existing tests in `test_stdlib_discovery.py` test the `_find_stdlib()` function from `compiler.cli.main`, not the `_try_discover_stdlib_via_package()` method in `CompilationSession`.
- The `CompilationSession.discover()` method's `_try_discover_stdlib_via_package()` was never directly tested with a pip-installed wheel.
- Tests that do run `CompilationSession` always run from the source repository where the upward walk finds `stdlib/`.

### Why the Packaged Wheel Behaved Differently

- In the source repository, `stdlib/` is at the repo root, and the upward walk from any subdirectory finds it.
- In a pip wheel install, `stdlib/` is at `site-packages/stdlib/`, which is NOT in the upward walk path from the user's project directory.
- The importlib.metadata fallback was supposed to handle this, but the relative path bug prevented it from working.

---

## P1 — Version Synchronization

### Root Cause

The version was bumped from `1.1.0` to `1.1.1` in `pyproject.toml` and `compiler/_version.py`, but the wheel was never rebuilt and republished to PyPI. This left PyPI with stale `1.1.0` metadata while the source had `1.1.1`.

### Affected Files

| File | Version Before | Version After |
|------|---------------|---------------|
| `pyproject.toml` | `1.1.1` | `1.1.2` |
| `compiler/_version.py` | `1.1.1` | `1.1.2` |
| Wheel metadata | `1.1.0` (PyPI) | `1.1.2` (rebuilt) |

### Why Previous Validation Missed It

- The version bump was done in source but the CI/CD pipeline was not triggered to rebuild and republish the wheel.
- No automated check verified that `pip show` version matches `ail version` output.

---

## P1 — Doctor False Negatives

### Root Cause

The `check_stdlib_available()` function in `tools/ail_doctor/__main__.py` only checked if `_find_stdlib()` returned a directory with `.ail` files. It did NOT verify that the stdlib modules could actually be resolved by the `ModuleResolver`. This meant it reported "OK" even when the runtime couldn't find the modules.

Additionally, the `detect_installation()` function correctly detected the package, but the stdlib check was disconnected from the actual module resolution path.

### Affected Files

| File | Change |
|------|--------|
| `tools/ail_doctor/__main__.py` | `check_stdlib_available()` now verifies key modules resolve via `ModuleResolver` |

### Why Previous Validation Missed It

- The doctor tests (`tests/test_ail_doctor.py`) test the doctor in the source repository where stdlib is always found.
- No test simulates a pip-installed environment where stdlib discovery fails but the directory exists.
