# M94 Investigation Report

## Overview

Independent external validation of AILang v1.1.3 completed with verdict: **READY WITH MINOR OBSERVATIONS**

This document summarizes the investigation and resolution of the three observations.

---

## Observation Summary

| # | Observation | Priority | Status |
|---|-------------|----------|--------|
| 1 | Stdlib Module Resolution (MOD003) | Highest | **CONFIRMED BUG - FIXED** |
| 2 | Developer Tool Discoverability | Medium | **NOT A BUG - INTENDED DESIGN** |
| 3 | License Consistency | Medium | **NOT A BUG - CONSISTENT** |

---

## Investigation Method

Each observation was investigated using the following approach:

1. **Reproduce** - Attempt to reproduce the reported issue
2. **Verify** - Determine if it is an actual bug or an environment/setup issue
3. **Evidence** - Collect evidence before making any changes
4. **Fix** - Make smallest correct changes if confirmed bug
5. **Document** - Ensure no regressions and document findings

---

## Detailed Findings

### Observation 1: Stdlib Module Resolution (Highest Priority)

**Reported Issue:** Repository examples importing stdlib modules fail with MOD003 because ModuleResolver does not search the installed package's stdlib directory.

**Investigation:**
- Created test file with stdlib imports (`import string;`)
- Ran from temp directory (outside project tree)
- **Result:** MOD003 confirmed - `Module not found: string`

**Root Cause Identified:**
The `ModuleResolver._candidate_roots()` method in `compiler/compilation/resolution.py` walks upward from the source file's directory looking for `stdlib/` directories, but it never searches the installed package's stdlib location.

The `_find_stdlib()` function in `compiler/cli/main.py` correctly handles finding the stdlib for CLI execution, but `ModuleResolver` used for compilation did not have equivalent logic.

**Fix Applied:**
Added `_find_stdlib_root()` function to `resolution.py` that mirrors the logic in `main.py:_find_stdlib()`. This function:
1. Finds the compiler package location
2. Checks for stdlib next to it (installed wheel case)
3. Falls back to site-packages if not found

Updated `_candidate_roots()` to include the installed stdlib as a fallback.

**Bug in Original Fix:**
Initial implementation used `parent.parent.parent` (3 levels up from compiler/__init__.py) which was incorrect. Fixed to use `parent.parent` (2 levels).

**Verification:**
- Test from temp directory: `import string;` now resolves correctly
- Multiple stdlib modules tested: `string`, `math`, `list`, `map`, `json` - all work
- All 14 module resolution tests pass
- All 1014 pytest tests pass

### Observation 2: Developer Tool Discoverability

**Reported Issue:** Tools exist, execute, and are installed, but are only accessible as Python modules.

**Investigation:**
- Reviewed `pyproject.toml` console_scripts
- Checked CLI dispatch in `compiler/cli/main.py`
- Tested tool invocation via `ail <tool>` commands

**Finding: NOT A BUG**

The validator's observation is incorrect. The tools ARE accessible as standalone commands through the `ail` CLI:

| Tool | Command | Status |
|------|---------|--------|
| heal | `ail heal` | Working |
| doctor | `ail doctor` | Working |
| docs | `ail docs` | Working |
| context | `ail context` | Working |
| static-analyzer | `ail static-analyzer` | Working |
| benchmark | `ail benchmark` | Working |
| testgen | `ail testgen` | Working |
| mcp | `ail mcp` | Working |

The CLI uses `_run_dx_tool()` helper function to dispatch to the tool modules. This is the **intended design (Option B)** - tools are invoked via `ail <tool>` subcommands, not as standalone console scripts.

**Evidence:**
```
$ ail doctor --help
# Runs tools.ail_doctor via subprocess
```

The validator may have been testing direct invocation as `python -m tools.ail_doc_verify` which also works but is not the primary interface.

### Observation 3: License Consistency

**Reported Issue:** Repository has MIT license, PyPI metadata has Apache-2.0.

**Investigation:**
- Reviewed root `LICENSE` file
- Reviewed `pyproject.toml` license field
- Checked PyPI METADATA in installed package
- Searched repository for license references

**Finding: NOT A BUG**

The validator's observation was based on incorrect information. The actual license is **Apache-2.0** consistently:

| Location | License | Status |
|----------|---------|--------|
| LICENSE file | Apache-2.0 | Correct |
| pyproject.toml | Apache-2.0 | Correct |
| README.md badge | Apache 2.0 | Correct |
| PyPI METADATA | Apache-2.0 | Correct |

**Historical Note:**
Archived documents reference MIT license because the project was originally MIT-licensed and changed to Apache-2.0 at some point (as noted in `extensions/vscode-ailang/CHANGELOG.md`: "License changed from MIT to Apache-2.0"). All current references are Apache-2.0.

---

## Regression Testing

After the fix for Observation 1:

| Test Suite | Result |
|------------|--------|
| pytest tests/ (1014 tests) | All passed |
| test_module_resolution.py (14 tests) | All passed |
| Module resolution from temp directory | Fixed - MOD003 resolved |

---

## Recommendation

**READY FOR PATCH RELEASE (v1.1.4)**

Only Observation 1 required a code change. The change is minimal, targeted, and has been verified to fix the bug without introducing regressions.

Observations 2 and 3 are not bugs - they are based on incorrect observations or outdated information.

---

## Files Changed

| File | Change |
|------|--------|
| `compiler/compilation/resolution.py` | Added `_find_stdlib_root()` function; Updated `_candidate_roots()` to include installed stdlib as fallback |

**No new files created. No documentation changes required for the fix itself.**