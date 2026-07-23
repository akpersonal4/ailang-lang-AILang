# Changelog

## v1.1.2 — M84R.3 Release Engineering & Packaging Fix

**Date:** 2026-07-22

### Fixed

#### P0 — Standard Library Module Resolution (MOD003)

- **Root cause:** `importlib.metadata` RECORD file contains relative paths (e.g., `stdlib/math.ail`), but the code used `_Path(parts[0])` which resolved them against the current working directory instead of the distribution's installation location.
- **Fix:** Changed `_Path(parts[0])` to `dist.locate_file(parts[0])` in `compiler/compilation/session.py` line 220. This resolves relative RECORD paths against the distribution's installation directory.
- **Impact:** `import math`, `import string`, `import list`, `import map`, `import json`, and all other stdlib modules now work correctly when installed via `pip install ailang-lang` and run from a non-repository directory.

#### P1 — Version Synchronization

- **Root cause:** Version was bumped to 1.1.1 in source but the wheel was never rebuilt and republished to PyPI, leaving stale 1.1.0 metadata.
- **Fix:** Bumped version to 1.1.2 in `compiler/_version.py` and `pyproject.toml`. Rebuilt wheel.
- **Impact:** All version sources now match: `compiler._version.py` = 1.1.2, `pyproject.toml` = 1.1.2, `pip show` = 1.1.2, `ail version` = v1.1.2.

#### P1 — Doctor Stdlib Detection

- **Root cause:** `check_stdlib_available()` in `tools/ail_doctor/__main__.py` only checked if the stdlib directory existed, not whether modules could actually be resolved.
- **Fix:** Added `ModuleResolver` verification that attempts to resolve 5 key modules (math, string, list, map, json) and requires at least 3 to succeed before reporting "OK".
- **Impact:** `ail doctor` no longer reports false positives for stdlib availability. Correctly detects when stdlib modules cannot be resolved at runtime.

### Files Changed

| File | Lines | Description |
|------|-------|-------------|
| `compiler/compilation/session.py` | 1 | Fixed relative path resolution in importlib.metadata fallback |
| `compiler/_version.py` | 1 | Bumped version to 1.1.2 |
| `pyproject.toml` | 1 | Bumped version to 1.1.2 |
| `tools/ail_doctor/__main__.py` | ~15 | Added ModuleResolver verification to stdlib check |

**Total: 4 files, ~18 lines changed**

### Tests

- Smoke test passed in clean venv with built wheel
- All 8 mandatory smoke test steps passed
- No regressions introduced

---

## v1.1.1

### M83I — Enterprise Validation Fixes

- **`ail rename` project root detection**: Fixed `ail rename` to detect the user's project root by walking CWD upward for `ail.toml` or `.ail` markers, instead of using the AILang package's stdlib parent. Renaming now correctly scans the user's project files.
- **Unknown flag handling**: `ail --invalid-flag` now reports `Error: unknown option '--invalid-flag'` with a general usage hint, instead of dispatching to `cmd_run` which showed the run-specific usage.
- **SEM001 diagnostic location consistency**: Pre-registration of module exports now sets `file_path` and source text on the symbol table, so duplicate declaration errors always include the source file path.
- **LEX002 cascade suppression**: Unterminated string errors (LEX002) now suppress downstream parser cascade errors (PAR001), reducing diagnostic noise from 7+ errors to 1.
- **SEM003/TYP011 deduplication**: The type checker now skips TYP011 (arity mismatch) when SEM003 (semantic arity check) already reported the same error, eliminating confusing dual error codes.
- **Suggested fixes for LEX002 and SEM001**: Added actionable next-step suggestions ("Add a closing quote..." for LEX002, "Rename one of the duplicate declarations..." for SEM001).
- **MOD003 module-not-found diagnostic**: Import resolution failures now emit MOD003 (Module not found) instead of silently falling through to MOD004 (Symbol not found in module).

### Tests

- 16 new regression tests covering all 7 fixes (test_m83i_fixes.py)
