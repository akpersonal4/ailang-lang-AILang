# M84R Test Report

## Test Environment

- Python: 3.11.15
- Platform: Windows 11
- AILang version: 1.1.1

## Test Results

### 1. Stdlib Module Resolution (I-1)

| Test | Steps | Expected | Actual | Result |
|------|-------|----------|--------|--------|
| Default scaffold works | `ail new demo && cd demo && ail run main.ail` | Prints "Hello, AILang!" | Prints "Hello, AILang!" | PASS |
| Full scaffold with imports | `ail new demo --full && cd demo && ail run main.ail` | Prints welcome + loads sample data | Prints welcome + loads sample data | PASS |
| `native_to_float` registered | Import and call `__native_to_float("10.5")` | Returns 10.5 | Returns 10.5 | PASS |
| `native_to_int` unchanged | Import and call `__native_to_int("42")` | Returns 42 | Returns 42 | PASS |

### 2. `ail doctor` (I-2)

| Test | Steps | Expected | Actual | Result |
|------|-------|----------|--------|--------|
| No crash in AILang repo | `ail doctor` from repo root | Shows full repo health report | Shows full repo health report | PASS |
| No crash from user project | `ail doctor` from user project dir | Shows user-facing diagnostics | Shows user-facing diagnostics | PASS |
| KeyboardInterrupt handled | Ctrl+C during doctor | "Doctor check cancelled" message | "Doctor check cancelled" message | PASS |
| Exception handled | Invalid state | Error message + bug report URL | Error message + bug report URL | PASS |

### 3. `convert.to_number` (I-3)

| Test | Input | Expected | Actual | Result |
|------|-------|----------|--------|--------|
| Decimal string | `convert.to_number("10.5")` | 10.5 (float) | 10.5 | PASS |
| Integer string | `convert.to_number("42")` | 42.0 (float) | 42.0 | PASS |
| Integer value | `convert.to_number(42)` | 42.0 (float) | 42.0 | PASS |
| Float value | `convert.to_number(3.14)` | 3.14 (float) | 3.14 | PASS |
| `to_int` unchanged | `convert.to_int("42")` | 42 (int) | 42 | PASS |

### 4. `ail install`/`ail add` Project Detection (I-4)

| Test | Steps | Expected | Actual | Result |
|------|-------|----------|--------|--------|
| AIL_PROJECT_ROOT set | Check env var in subprocess | Project root passed to package manager | Env var correctly set | PASS |
| `cmd_add` receives project_dir | Check `cmd_add` in `__main__.py` | Reads AIL_PROJECT_ROOT | Reads AIL_PROJECT_ROOT | PASS |
| `cmd_remove` receives project_dir | Check `cmd_remove` in `__main__.py` | Reads AIL_PROJECT_ROOT | Reads AIL_PROJECT_ROOT | PASS |

### 5. `ail heal` File Detection (I-7)

| Test | Steps | Expected | Actual | Result |
|------|-------|----------|--------|--------|
| File with errors | `ail heal bad_file.ail` | Auto-detects topics from errors | Shows relevant heal topics | PASS |
| File without errors | `ail heal good_file.ail` | "No errors detected" message | Shows "No errors detected" | PASS |
| Topic name still works | `ail heal forward_reference` | Shows forward reference help | Shows forward reference help | PASS |
| No args | `ail heal` | Lists available topics | Lists available topics | PASS |

### 6. Documentation Updated

| Document | Updated | Content Verified |
|----------|---------|-----------------|
| README.md | Yes | Quick start uses `ail new` workflow |
| GETTING_STARTED.md | Yes | Project setup, module imports documented |
| INSTALLATION.md | Yes | pip install primary, troubleshooting expanded |
| STDLIB_REFERENCE.md | Yes | `to_number` returns float |
| MODULE_SYSTEM.md | Yes | Full resolution algorithm documented |

### 7. Regression Tests

| Test Suite | Tests | Pass | Fail | Result |
|------------|-------|------|------|--------|
| test_validation.py | 18 | 18 | 0 | PASS |

## Summary

- **Total tests executed:** 27+ (unit, integration, regression)
- **Passed:** 27+
- **Failed:** 0
- **No regressions** in existing test suite
