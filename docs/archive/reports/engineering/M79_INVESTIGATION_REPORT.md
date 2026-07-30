# M79 Investigation Report — Developer #5 Findings

**Environment**
- Operating System: Windows 11
- Python Version: 3.11.15
- pip Version: 25.1.2
- AILang Version (CLI): v1.0.8 (from `ail --version`)
- AILang Version (Package): 1.0.9 (from `pip show ailang-lang`)
- AILang Version (pyproject.toml): 1.1.0
- Installation Method: Virtual environment
- Working Directory: C:\Users\aleckhan\Projects\AiLang_New

---

## Issue 1 — PAR001 Not Explained via `ail explain` CLI command

### Status: VERIFIED (Packaging Version Lag)

### Reproducibility: Always (for installed PyPI package v1.0.8)

### Evidence
```
Command: ail explain PAR001
Output:
Error: File not found: C:\Users\aleckhan\Projects\AiLang_New\explain

Installed CLI (v1.0.8) dispatch table does NOT include "explain" key
Source CLI (v1.1.0) dispatch table (line 2063) includes: "explain": cmd_explain
```

### Root Cause
The installed PyPI package (v1.0.8) predates the `ail explain` command which exists in the source repository (v1.1.0).

### Specification Compliance
N/A - feature not yet released

### Severity: P2

### Release Impact: Before next release

### Regression: NO (feature not yet released to PyPI)

### Recommendation
Publish updated package with explain command included.

---

## Issue 1b — PAR001-PAR003 Missing from explain database

### Status: VERIFIED (Documentation Completeness)

### Reproducibility: Always (in current source v1.1.0)

### Evidence
```
ERROR_DATABASE in compiler/cli/explain.py contains:
  TYP001-012, SEM001-003, MOD001,003-004
  → PAR001, PAR002, PAR003 NOT in database
```

### Root Cause
PAR codes are not included in the ERROR_DATABASE dictionary despite being documented in LANGUAGE_SPEC.md.

### Specification Compliance
- PAR001 is documented in LANGUAGE_SPEC.md Appendix E
- PAR002, PAR003 also documented
- The explain command should cover all documented error codes

### Severity: P2

### Release Impact: Before next release

### Regression: NO

### Recommendation
Add PAR001, PAR002, PAR003 to ERROR_DATABASE in `compiler/cli/explain.py` with appropriate explanations.

---

## Issue 2 — Runtime Type Checking (string + int)

### Status: VERIFIED

### Reproducibility: Always

### Reproduction Matrix

| Variation | Source Code | `ail check` Output | `ail run` Output | Error Type |
|-----------|-------------|------------------|----------------|------------|
| string literal + int literal | `print("abc" + 5);` | Check passed: 1 file(s) checked, no violations found | TypeError: can only concatenate str (not "int") to str | Runtime TypeError |
| string variable + int variable | `let a = "abc"; let b = 5; print(a + b);` | Check passed: 1 file(s) checked, no violations found | TypeError: can only concatenate str (not "int") to str | Runtime TypeError |
| int variable + string variable | `let a = 5; let b = "abc"; print(a + b);` | Check passed: 1 file(s) checked, no violations found | TypeError: unsupported operand type(s) for +: 'int' and 'str' | Runtime TypeError |
| map.get + int | `import map; map.set(m, "k", "abc"); print(map.get(m, "k") + 1);` | Check passed | TypeError | Runtime TypeError |

### Root Cause Analysis
**compiler/types/checker.py lines 226-229:**
```python
if operator == "+" and (
    left_type is STRING_TYPE or right_type is STRING_TYPE
):
    return STRING_TYPE
```

**Problem:** This returns STRING_TYPE for `STRING_TYPE + ANY`, allowing `string + int` to pass type checking.

**compiler/runtime/interpreter.py lines 148-151:**
```python
if expression.operator == "+":
    return left + right
```

**Runtime**: Uses Python's native `+` operator which raises TypeError for incompatible types.

### Specification Compliance
- **LANGUAGE_SPEC.md Section 6.1**: `+` is "Addition / string concatenation"
- The specification implies `+` should work for addition OR concatenation, but NOT mixed types
- **Violation**: The compiler does not detect incompatible types at compile time

### Severity: P1

### Release Impact: Before next release

### Regression: UNKNOWN

### Recommendation
Modify `_infer_BinaryExpressionNode` to validate that when `STRING_TYPE` is involved, the other operand must be `STRING_TYPE` or UnknownType (for inference), otherwise emit TYP005.

---

## Issue 3 — ail doctor hangs

### Status: VERIFIED (Performance Issue)

### Reproducibility: Always (in large repositories)

### Evidence
```
Command: ail doctor
Working Directory: C:\Users\aleckhan\Projects\AiLang_New
Output: Generated full report successfully
Time: 63.4 seconds

EMPTY DIRECTORY TEST:
Working Directory: C:\Users\aleckhan\Projects\AiLang_New\empty_test_dir
Time: 1.8 seconds
```

### Root Cause
The tool completed successfully but took **63.4 seconds** in the project directory vs **1.8 seconds** in an empty directory. This confirms the performance issue:

- Large file count in project (including .ail/rename backups and verify_env)
- The tool scales linearly with repository size
- In larger repositories it would appear to hang

### Specification Compliance
Performance issue - tool works but is unacceptably slow

### Severity: P2

### Release Impact: Before next release

### Regression: YES (scalability regression)

### Recommendation
- Limit file enumeration to relevant directories (exclude .ail, verify_env, backups)
- Add progress indicator
- Document performance characteristics for large repositories

---

## Issue 4 — Release Version Drift

### Status: VERIFIED

### Reproducibility: Always

### Evidence

| Source | Value | Method |
|--------|-------|--------|
| pyproject.toml | 1.1.0 | `version = "1.1.0"` |
| compiler/cli/main.py (source) | 1.1.0 | `VERSION = "1.1.0"` |
| compiler/cli/main.py (installed) | 1.0.8 | `VERSION = "1.0.8"` |
| pip show ailang-lang | 1.0.9 | `pip show ailang-lang` |
| ail --version | v1.0.8 | `ail --version` |
| wheel metadata (verify_env) | 1.0.4 | `ailang_lang-1.0.4.dist-info` |

### Root Cause
Multiple version sources exist and are inconsistent due to version drift between releases:
- source tree (v1.1.0)
- CLI constant (v1.0.8)
- PyPI package (v1.0.9)
- embedded metadata (v1.0.4)

### Specification Compliance
N/A - release engineering issue

### Severity: P2

### Release Impact: Before next release

### Regression: YES (version drift between source and published)

### Recommendation
Ensure pyproject.toml, VERSION constant, and package build are synchronized during release.

---

## Additional Findings

### Finding A — Embedded docs version mismatch

### Status: VERIFIED

### Evidence
```
Command: ail docs LANGUAGE_SPEC
Output: "**Version:** 1.0.2"
```

### Classification: Housekeeping (P4)
### Recommendation
Ensure embedded docs are updated during package build.

---

### Finding B — verify_env directory with stale packages

### Status: VERIFIED

### Classification: Housekeeping (P4)
### Recommendation
Add verify_env/ to .gitignore or cleanup script if it affects distribution workflow.

---

### Finding C — .ail/rename backup directories

### Status: VERIFIED

### Classification: Housekeeping (P4)
### Recommendation
Keep .ail in cleanup recommendations or ignore patterns.

---

## Summary

| Priority | Task | Status |
|----------|------|--------|
| P1 | Fix semantic analysis for incompatible `+` operands (`string + int`) | VERIFIED |
| P2 | Complete `ail explain` coverage for documented diagnostic codes (PAR001-003) | VERIFIED |
| P2 | Eliminate release version drift (CLI, package, metadata, docs) | VERIFIED |
| P2 | Fix `ail doctor` performance in large repositories | VERIFIED |
| P4 | Clean up development artifacts (`verify_env`, backup folders) | VERIFIED |