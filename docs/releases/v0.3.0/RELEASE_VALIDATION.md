# v0.3.0 Release Validation Report

**Date:** 2026-07-07
**Version:** 0.3.0 (minor)
**Scope:** DX-004 Benchmark Runner — automated benchmark execution, reporting, and regression detection

---

## 1. Test Suite

**Command:** `python -m pytest tests/ --tb=short -q`

| Test Group | Count | Status |
|------------|:-----:|:------:|
| Core compiler tests (AST, IR, lexer, parser, runtime, scope cache) | 576 | **PASS** |
| Benchmark, stress, AI validation | 82 | **PASS** |
| **DX-004 acceptance (11) + regression (4) + AI validation (4)** | **19** | **PASS** |
| **Total** | **677** | **PASS** |

All 677 pytest tests pass. 19 new tests added for DX-004. No test regressions detected.

---

## 2. DX-004 Validation (`ail benchmark`)

**Command:** `python tests/dx_tool_004_acceptance_test.py`

| Test | Status |
|------|:------:|
| Tool runs successfully (`--help`) | **PASS** |
| Output files created (MD + JSON) | **PASS** |
| Deterministic output (SHA-256 match) | **PASS** |
| JSON structure valid | **PASS** |
| `--suite quick` (2 apps: dice_roller, hangman_game) | **PASS** |
| `--app <path>` single app mode | **PASS** |
| `--baseline` save + `--compare` baseline | **PASS** |
| `--memory` memory measurement mode | **PASS** |
| `--threshold` configurable regression threshold | **PASS** |
| Performance under 120s for quick suite | **PASS** |
| `--repeat` configurable repetition count | **PASS** |

**All 11 tests: PASS**

---

## 3. Regression Detection

**Command:** `python tests/dx_tool_004_regression_test.py`

| Test | Status |
|------|:------:|
| Regression triggers on inflated baseline | **PASS** |
| No false positive with matching baseline | **PASS** |
| Correct exit code precedence (regression > failure > pass) | **PASS** |
| Suite definitions (quick, canonical, full) resolve correctly | **PASS** |

**All 4 tests: PASS**

---

## 4. AI Validation

**Command:** `python tests/dx_tool_004_ai_validation.py`

| Test | Status |
|------|:------:|
| Basic benchmark mode | **PASS** |
| Exit code mapping | **PASS** |
| Repetition / timing | **PASS** |
| Baseline / compare | **PASS** |

**All 4 tests: PASS**

---

## 5. Tool Output Structure

**Output directory:** `generated/benchmarks/`

| File | Format | Validated |
|------|--------|:---------:|
| `BENCHMARK_REPORT.md` | Markdown report | **PASS** |
| `BENCHMARK_REPORT.json` | Structured JSON | **PASS** |

JSON schema includes:
- `metadata` (version, timestamp, args)
- `benchmarks` array with `name`, `file`, `runs`, `timings` (min/avg/median/max), `status`, `error`
- `summary` with total/duration/passed/failed/regressed counts

---

## 6. Exit Code Design

| Exit Code | Meaning | Validated |
|:---------:|---------|:---------:|
| 0 | All benchmarks passed | **PASS** |
| 1 | One or more benchmarks failed | **PASS** |
| 2 | Regression detected (≥threshold) | **PASS** |
| 3 | Internal tool error | **PASS** |

---

## 7. Change Summary

### Files added:

| File | Purpose |
|------|---------|
| `tools/ail_benchmark/__init__.py` | Package init |
| `tools/ail_benchmark/__main__.py` | CLI entry point (30 LOC) |
| `tools/ail_benchmark/discovery.py` | Suite definitions, app discovery (37 LOC) |
| `tools/ail_benchmark/runner.py` | Benchmark execution, measurement pipeline, timing/memory (102 LOC) |
| `tools/ail_benchmark/compare.py` | Baseline save/compare, regression detection (57 LOC) |
| `tools/ail_benchmark/reporter.py` | Markdown + JSON report generation (67 LOC) |
| `tests/dx_tool_004_acceptance_test.py` | 11 acceptance tests (112 LOC) |
| `tests/dx_tool_004_regression_test.py` | 4 regression detection tests (67 LOC) |
| `tests/dx_tool_004_ai_validation.py` | 4 AI validation tests (67 LOC) |
| `generated/benchmarks/` | Benchmark output directory |

### Files modified:

| File | Change |
|------|--------|
| `CHANGELOG.md` | Added v0.3.0 section with DX-004 entry |
| `DEVELOPMENT_STATUS.md` | Updated version to v0.3.0, DX-004 completed |
| `PROJECT_MEMORY.md` | Added M12 milestone entry for DX-004 |

---

## 8. Regression Analysis

### No regressions detected in:
- All 658 pre-existing pytest tests pass (same as v0.2.1 baseline)
- Compiler AST/IR/CST unchanged
- Runtime unchanged
- Stdlib unchanged
- Existing CLI tools (ail context, ail doctor, ail static_analyzer) unchanged
- All 43+ apps unchanged
- All 10 canonical benchmarks unchanged

### Regressions found:
- **None**

---

## 9. Performance

Benchmark runner itself adds negligible overhead. Subprocess execution ensures measurements reflect actual AILang runtime.

Quick suite (2 apps, 3 repetitions each) completes in under 120s.

---

## 10. Architectural Decisions (DX-004)

| Decision | Rationale |
|----------|-----------|
| **Subprocess-based execution** | Measures real wall-clock time, no Python instrumentation overhead |
| **Structured JSON + human Markdown** | Dual output supports automated CI parsing and human review |
| **Fault-tolerant execution** | One failure doesn't abort suite — essential for CI |
| **Exit code separation (0/1/2/3)** | CI can distinguish pass from failure from regression from internal error |
| **Configurable repetition** | Default 3× balances statistical confidence vs. runtime cost |
| **Measurement pipeline pattern** | Timer/Memory extensible for future CPU/profiling metrics |
| **Baseline saved as comparison JSON** | Simple diff-based regression detection without a database |

---

## Overall Verdict

| Check | Status |
|-------|:------:|
| All tests passed (677/677) | **PASS** |
| DX-004 acceptance (11 tests) | **PASS** |
| Regression detection (4 tests) | **PASS** |
| AI validation (4 tests) | **PASS** |
| Exit codes correct (0/1/2/3) | **PASS** |
| JSON + Markdown output valid | **PASS** |
| No regressions in existing code | **PASS** |
| Quick suite under 120s | **PASS** |

**Release readiness:**

**APPROVED**

Known pre-existing issues (not caused by this release):
- DX-003 directory analysis timeout for very large repositories — configurable via `--timeout` (default: 300s)
- `ail fmt` false positive on SEMICOLON token — tracked in DEVELOPMENT_STATUS.md
- Source line numbers not included in error messages

---

*Generated by v0.3.0 Release Validation. All measurements taken on Windows 11, Python 3.11.15, Intel Core i7.*
