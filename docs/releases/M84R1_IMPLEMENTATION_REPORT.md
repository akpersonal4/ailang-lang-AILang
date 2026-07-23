# M84R1 Implementation Report

**Milestone:** M84R.1 — Final Remediation Before Release
**Date:** 2026-07-22
**Version:** v1.1.2 (target)

---

## Summary

Completed the final release-quality remediation before public release to GitHub and PyPI. Addressed all P0 and P1 defects identified by independent M85 evaluation and manual verification. All changes are DX stabilization only — no language features, no syntax changes, no compiler modifications.

---

## Changes Made

### P0-1: Fix Incorrect Package Detection

**Problem:** `ail doctor` showed `ailang package: NOT INSTALLED (run: pip install -e .)` even when `pip install ailang-lang` was already installed. The old `check_ail_package()` tried `import ailang` which imported a stale v0.10.0 package, not `ailang-lang`.

**Solution:** Replaced `check_ail_package()` with a comprehensive `detect_installation()` function that:

1. Uses `importlib.metadata.distribution("ailang-lang")` to find the correct distribution
2. Checks `direct_url.json` to distinguish editable vs PyPI installs
3. Falls back to checking if `compiler` module runs from source tree (not site-packages)
4. Provides context-aware install recommendations via `get_install_recommendation()`

**Detection modes:**
| Method | When Detected | Recommendation |
|--------|--------------|----------------|
| `pypi` | `direct_url.json` present, not editable | `pip install ailang-lang` |
| `editable` | `direct_url.json` present, `dir_info.editable=true` | `pip install ailang-lang` |
| `source_checkout` | No `direct_url.json`, compiler in source tree | `pip install -e .` |
| `not_installed` | Distribution not found, not source tree | `pip install ailang-lang` |

**Files changed:**
- `tools/ail_doctor/__main__.py` — Added `detect_installation()`, `_detect_source_checkout()`, `_is_running_from_source_tree()`, `get_install_recommendation()`

**Tests added:**
- `test_detect_installation_returns_dict`
- `test_detect_installation_finds_version`
- `test_get_install_recommendation_pypi`
- `test_get_install_recommendation_editable`
- `test_get_install_recommendation_not_installed`
- `test_get_install_recommendation_source_checkout`

### P0-2: Repository Mode vs Project Mode

**Problem:** Running `ail doctor` inside the AILang repository triggered full repository analysis (orphan documents, broken links, archive candidates). Normal developers received developer-facing output.

**Solution:** Split `ail doctor` into two explicit modes:

- `ail doctor` (default) — Project Health: Python version, CLI status, package detection, stdlib availability, project file checks
- `ail doctor --repo` — Repository Health: Full 15-check analysis with health score, version consistency, orphan docs, etc.

Repository diagnostics only appear with the `--repo` flag. The tool uses `argparse` for flag parsing.

**Files changed:**
- `tools/ail_doctor/__main__.py` — Rewrote `generate_report()` to accept `repo_mode` parameter. Added `argparse` to `main()`.
- `compiler/cli/main.py` — Updated `cmd_doctor()` docstring to document `--repo` flag

### P0-3: Improve Doctor Output

**Problem:** Output mixed Project Health and Repository Health in a single report with no clear separation.

**Solution:** Two distinct report formats:

**Project Health (default):**
```
# AILang Doctor
## Project Health
### Environment
### Standard Library
### Project
### Summary
```

**Repository Health (`--repo`):**
```
# AILang Doctor Report
## Installation
## Repository Health Score
## Components
## Warnings
## Errors
## Recommendations
## Archive Candidates
## Duplicate Candidates
## Missing References
## Version Consistency
## Next Steps
```

### P1-4: Verify ail heal Commands

**Problem:** `ail heal env_setup` recommended `pip install -e .` for all users, including PyPI users.

**Solution:**
1. Changed `env_setup` topic to recommend `pip install ailang-lang` (correct for 99% of users)
2. Added 2 new topics: `map_safety` and `string_concat` (common AILang patterns)
3. Updated file analysis to handle more error codes
4. All 9 topics verified working

**Files changed:**
- `tools/ail_heal/__main__.py` — Updated `env_setup` content, added `map_safety` and `string_concat` topics

**Tests added:**
- `test_heal_map_safety_topic`
- `test_heal_string_concat_topic`
- Updated `test_heal_env_setup_topic` to assert `pip install ailang-lang` (not `pip install -e .`)

### P1-5: Improve Diagnostics

**Problem:** Doctor and heal tools recommended `pip install -e .` regardless of installation context.

**Solution:** Context-aware guidance throughout:
- Project mode: Never mentions `pip install -e .`
- Source checkout: Correctly recommends `pip install -e .`
- PyPI/editable: Recommends `pip install ailang-lang`
- `ail heal env_setup`: Recommends `pip install ailang-lang`

### P2: DX Review

**Additional improvements:**
- Updated CLI `--help` text: doctor now says "Check project health (use --repo for repository analysis)"
- Updated `cmd_doctor()` and `cmd_heal()` docstrings with accurate usage
- All path leakage prevention tests pass (no developer-specific paths in output)

---

## Files Modified

| File | Lines Changed | Purpose |
|------|:------------:|---------|
| `tools/ail_doctor/__main__.py` | ~650 (rewritten) | Package detection, mode separation, improved output |
| `tools/ail_heal/__main__.py` | ~300 (rewritten) | Fixed env_setup, added 2 topics |
| `compiler/cli/main.py` | ~10 | Updated help text and docstrings |
| `tests/test_ail_doctor.py` | ~100 (rewritten) | 8 tests for new doctor behavior |
| `tests/test_dx_improvements.py` | ~50 | Added package detection tests, updated heal tests |

---

## Verification

- 42/42 tests pass (8 doctor + 34 dx_improvements)
- All 9 heal topics verified individually
- `ail doctor` project mode: correct output, no path leakage
- `ail doctor --repo` mode: correct output, full repository analysis
- `ail heal env_setup`: recommends `pip install ailang-lang` (not `pip install -e .`)
- `ail new demo && ail run main.ail`: end-to-end flow works
- Path leakage prevention: all tests pass
