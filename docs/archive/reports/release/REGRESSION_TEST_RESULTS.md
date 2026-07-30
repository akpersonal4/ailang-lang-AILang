# Regression Test Results

**Package:** ailang-lang v1.1.6
**Date:** 2026-07-28
**Environment:** Python 3.11.15, Windows 11, pytest

---

## Full Test Suite Results

```
python -m pytest -q --timeout=120 2>&1 | tail -5
1128 passed, 80 warnings in 113.17s (0:01:53)
```

> Note: 8 tests in `dx_tool_003_acceptance_test.py` require longer timeouts and pass individually with `--timeout=300`. Total: 1136 tests.

```
python -m pytest tests/dx_tool_003_acceptance_test.py -q --timeout=120
8 passed, 8 warnings in 67.14s (0:01:07)
```

**Combined: 1136 passed, 0 failed**

---

## Previously Failing Tests

| Test | Before | After |
|------|--------|-------|
| `test_context_tool_prints_to_stdout` | FAILED (v1.1.4 assertion) | PASSED |
| `test_context_json_output` | FAILED (v1.1.4 assertion) | PASSED |
| `test_mcp_initialize` | FAILED (v1.1.4 assertion) | PASSED |
| `test_mcp_get_language_context` | FAILED (v1.1.4 assertion) | PASSED |
| `test_package_json_version` | FAILED (v1.1.4 assertion) | PASSED |

---

## Regression Checks

### No Regressions Found

| Feature | Status |
|---------|--------|
| Core compilation (run, build) | PASS |
| Forward reference detection | PASS |
| Type checking | PASS |
| Stdlib module resolution (MOD003) | PASS |
| Formatter | PASS |
| MCP server | PASS |
| Error diagnostics | PASS |
| `ail check` vs `ail build` consistency | PASS |
| Unknown flag handling | PASS |
| `ail explain` command | PASS |
| `ail heal` command | PASS |
| `ail fmt` idempotency | PASS |
| `ail test` command | PASS |
| `ail new` command | PASS |
| `ail context --json` | PASS |
| `ail static-analyzer` | PASS |
| `ail benchmark` | PASS |
| `ail rename` | PASS |
| `ail doctor` | PASS |
| `ail docs` | PASS |

---

## Test Count Validation

| Source | Claim | Actual |
|--------|-------|--------|
| README.md badge | 1136 passing | 1136 ✓ |
| README.md text | 1136 tests | 1136 ✓ |
| CHANGELOG.md v1.1.6 | All 1136 tests | 1136 ✓ |

---

## Conclusion

**All 1136 tests pass with zero failures.** All previously failing tests (5 stale version assertions) are fixed. All 5 regressions identified in the M106 audit are resolved. No new regressions introduced.
