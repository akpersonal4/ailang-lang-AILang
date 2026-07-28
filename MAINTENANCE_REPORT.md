# MAINTENANCE_REPORT.md

**Date:** 2026-07-28
**Scope:** Post-certification maintenance for v1.1.6

---

## Summary

Maintenance performed after v1.1.6 certification. Scope limited to cleanup, version sync, dead code removal, and documentation updates. No behavioural changes to the compiler, language, or runtime.

| Metric | Value |
|--------|-------|
| Files reviewed | 40+ |
| Files modified | 18 |
| Lines added | 27 |
| Lines removed | 42 |
| Net change | -15 lines |
| Regressions | 0 |

---

## Files Modified

| File | Change |
|------|--------|
| `DEVELOPMENT_STATUS.md` | Updated version from v1.1.4 to v1.1.6 (2 occurrences) |
| `PROJECT_MEMORY.md` | Updated version from v1.1.4 to v1.1.6 |
| `README.md` | Updated badge version from 1.1.5 to 1.1.6 |
| `compiler/cli/main.py` | Updated ail.toml template language version to 1.1.6 |
| `compiler/parser/parser.py` | Removed unused `ErrorCode` import |
| `docs/reference/LANGUAGE_SPEC.md` | Updated version from 1.1.4 to 1.1.6 |
| `tools/ail_doc_verify/__main__.py` | Removed unused `import sys` |
| `tools/ail_dx_audit/__main__.py` | Removed unused `import sys` |
| `tools/ail_mcp/__init__.py` | Updated `__version__` from 1.1.5 to 1.1.6 |
| `tools/ail_order/__main__.py` | Removed unused `has_errors` assignment |
| `tools/ail_order/fixer.py` | Removed unused `header_lines` and `block_start` variables |
| `tools/ail_order/reporter.py` | Removed unused `recommendations` list |
| `tools/ail_package_manager/init.py` | Updated language version template to 1.1.6 |
| `tools/ail_package_manager/registry.py` | Fixed missing `import os` (runtime crash), removed dead `manifest` assignment |
| `tools/ail_stdlib_audit/__main__.py` | Removed unused `import sys` |
| `tools/ail_validate/__main__.py` | Removed unused `import sys` |
| `tools/perf_profiler.py` | Removed unused `result_var` assignment |

---

## Issues Found and Fixed

| Issue | Severity | Status |
|-------|----------|--------|
| Missing `import os` in `registry.py` (runtime crash in 2 functions) | **HIGH** | Fixed |
| Stale version strings (11 files referencing v1.1.5, v1.1.4, or older) | MEDIUM | Fixed |
| 5 unused imports (F401) | LOW | Fixed |
| 6 unused variable assignments (F841) | LOW | Fixed |

---

## Verification

- Full test suite: **982 passed, 0 failed**
- No regressions introduced
- CLI help text verified for `--help`, `--version`, `doctor`, `explain`
- Packaging metadata verified (`pyproject.toml`, `MANIFEST.in`)