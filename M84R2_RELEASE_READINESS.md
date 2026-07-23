# M84R.2 — Release Readiness

**Date:** 2026-07-22

---

## Release Gate Checklist

| # | Gate | Status | Evidence |
|:-:|------|:------:|----------|
| 1 | All reproduced P0 defects fixed | ✅ | Module resolver now falls back to bundled stdlib. Verified from non-repo directory. |
| 2 | All reproduced P1 defects fixed | ✅ | `list.sum` and `list.sum_by_key` correctly handle floats. Verified: 15.5+2.5+4.0=22.0. |
| 3 | P2 defects fixed or documented | ✅ | Not reproduced. `list.sort_by_key` works correctly. Polymorphic design is intentional. |
| 4 | `ail new` works without manual stdlib copying | ✅ | `ail new demo && cd demo && ail run main.ail` succeeds. |
| 5 | `ail run main.ail` works immediately after project creation | ✅ | Generated template builds and runs. |
| 6 | `list.sum()` returns correct floating-point results | ✅ | Float inputs return float, int inputs return int. |
| 7 | `list.sort_by_key()` behaves correctly | ✅ | Sorts maps by key in ascending order. |
| 8 | CLI version and package version are identical | ⚠️ | Source code: v1.1.1. Installed metadata: v1.1.0 (stale). Needs wheel rebuild. |
| 9 | Full regression suite passes | ✅ | 1017/1017 tests pass. Zero regressions. |
| 10 | No new regressions introduced | ✅ | All existing behavior preserved. |

---

## Changes Made

| File | Change |
|------|--------|
| `compiler/compilation/resolution.py` | Added `_bundled_stdlib_root()` fallback for stdlib resolution from installed packages |
| `compiler/runtime/builtins.py` | Fixed `list_sum()` and `list_sum_by_key()` to handle floating-point values correctly |

---

## Version Status

| Artifact | Version | Notes |
|----------|---------|-------|
| `pyproject.toml` | 1.1.1 | Correct |
| `compiler/_version.py` | 1.1.1 | Correct |
| `ail version` CLI | 1.1.1 | Correct |
| `pip show ailang-lang` | 1.1.0 | Stale metadata (needs rebuild) |

**Action required:** Rebuild wheel before publishing to PyPI.

---

## Decision

### **READY AFTER MINOR FIXES**

**Rationale:**

- P0 fix (module resolution) is correct and verified.
- P1 fix (float handling) is correct and verified.
- P2 is not a real issue — evaluator's claim was incorrect.
- All 1017 tests pass with zero regressions.
- The only remaining issue is the version metadata sync (`pip show` reports 1.1.0 instead of 1.1.1), which requires a wheel rebuild before publishing. This is a packaging step, not a code fix.

**Blocking item:** Rebuild and republish the `ailang-lang` wheel to PyPI to sync version metadata.
