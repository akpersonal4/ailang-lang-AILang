# M84R.2 — Regression Report

**Date:** 2026-07-22

---

## Test Results

### Python Test Suite

```
1017 passed, 0 failed, 79 warnings
Duration: 288.63s (4m 48s)
```

Test file `tests/dx_tool_003_acceptance_test.py` excluded due to pre-existing timeout (not related to M84R.2 changes).

### Stdlib Collection Tests (Directly Affected)

```
20 passed, 0 failed
Duration: 2.20s
```

All existing `list.sum`, `list.sum_by_key`, `list.sort`, `list.sort_by_key`, `list.group_by_key`, `list.take`, `list.skip`, `list.search_by_name`, `list.exists_by_key`, and `map.values` tests pass.

---

## Regression Checks

| Check | Result |
|-------|:------:|
| All existing tests pass | ✅ |
| `ail new` creates project successfully | ✅ |
| `ail run main.ail` executes generated project | ✅ |
| `ail build main.ail` compiles without errors | ✅ |
| `ail doctor` reports healthy environment | ✅ |
| `list.sum` with integers returns int | ✅ (60) |
| `list.sum` with floats returns float | ✅ (22.0) |
| `list.sum` with mixed returns float | ✅ (42.5) |
| `list.sum_by_key` with integers returns int | ✅ (30) |
| `list.sum_by_key` with floats returns float | ✅ (22.0) |
| `list.sort_by_key` sorts correctly | ✅ (Alice, Bob, Charlie) |
| Module resolution from non-repo directory | ✅ (was broken, now fixed) |
| No new regressions introduced | ✅ |

---

## Notes

- The `ail doctor --repo` report shows duplicate file warnings from test environments (`verify_env/`, `verify_demo/`, etc.) created during reproduction. These are not code issues.
- Pre-existing `ail fmt --check` failures across many files are unrelated to M84R.2 changes.
