# ROOT_CAUSE_ANALYSIS.md — M89

**Milestone:** M89 — External Validation Remediation  
**Date:** 2026-07-23

---

## Finding 1: README Version Mismatch (1.1.1 vs 1.1.2)

**Root cause:** When v1.1.2 was released, the README badge was not updated from 1.1.1. The version bump in `pyproject.toml` and `_version.py` was done, but the README badge is a static string that requires manual updating.

**Why not detected earlier:** The release process focuses on package metadata (pyproject.toml, _version.py) and CHANGELOG. The README badge is a separate markdown string that isn't validated by any automated check.

**Fix:** Updated README.md badge from `1.1.1` to `1.1.2`.

**Regression prevention:** The `ail release --verify` command should check README version consistency.

---

## Finding 2: Template Missing Semicolon

**Root cause:** The template string in `compiler/cli/main.py` had `return 0` without a semicolon. While the formatter auto-corrects this, the template should generate syntactically correct code.

**Why not detected earlier:** The template was created when semicolons on return statements were optional. The formatter's auto-correction masked the issue during manual testing.

**Fix:** Added semicolon to the template string: `return 0;`

**Regression prevention:** The template output should be verified as valid AILang without requiring formatting.

---

## Finding 3: Template Language Version Mismatch (0.3)

**Root cause:** The `_AIL_TOML_TEMPLATE` string used a hardcoded `version = "0.3"` for the language version. This was set when the template was created and never updated as the language versioned.

**Why not detected earlier:** The language version in ail.toml is informational and doesn't affect compilation. No automated check validates it against the package version.

**Fix:** Updated template to use `version = "1.1.2"`.

**Regression prevention:** Template version should be derived from `__version__` or validated during release.

---

## Finding 4: Official Examples Fail to Compile (member_access, recursive_map)

**Root cause (member_access):** The 3 member_access examples lacked `main()` functions and `print()` calls. They were pure declaration files that compiled but produced no output.

**Root cause (recursive_map):** The example defined a function named `map` which collided with the stdlib `map` module. The semantic analyzer treats this as a duplicate declaration (SEM001).

**Why not detected earlier:** The examples were tested individually and "worked" (exit code 0), but the lack of output and the SEM001 error weren't caught because the test methodology checked exit codes, not output content or build errors.

**Fix:** Rewrote member_access examples to include `main()` and `print()`. Renamed `map` function to `transform_list` in recursive_map.

**Regression prevention:** Example validation should include build verification and output content checks.

---

## Finding 5: Showcase Apps Fail to Build (hotel_management, kanban)

**Root cause:** Both apps defined top-level functions with names identical to stdlib builtins (`list_find_by_key`, `list_filter_by_key`, `list_filter_by_contains`, `list_copy`). The runtime resolves names by checking the global environment before builtins, so user-defined functions shadow stdlib functions, causing SEM001 or runtime failures.

**Why not detected earlier:** The apps were developed incrementally. When these helper functions were added, the stdlib didn't yet have functions with those exact names. The stdlib expanded over time, creating collisions that weren't caught.

**Fix:** Renamed all colliding functions to app-specific names (e.g., `hotel_find_by_key`, `kanban_copy_list`).

**Regression prevention:** The `ail check` command should detect stdlib name collisions and warn developers.

---

## Finding 6: CLI --help Inconsistency

**Root cause:** The 10 core commands used a custom argument parser that manually processed flags. The `--help` flag was not recognized and fell through to the "Unknown option" branch, printing to stderr and exiting with code 1.

**Why not detected earlier:** The DX tools (doctor, heal, explain) use argparse which has built-in --help support. The core commands were implemented before the argparse-based tools and never received --help support.

**Fix:** Added `--help`/`-h` detection at the start of each command's argument parsing.

**Regression prevention:** All new commands should be required to support `--help` with exit code 0.

---

## Finding 7: Silent Examples

**Root cause:** Examples were written as language feature demonstrations (showing syntax) rather than runnable programs. The focus was on showing how to write code, not on producing visible output.

**Why not detected earlier:** The examples compile and run (exit code 0). The test methodology checked for crashes, not for educational value.

**Fix:** Added `print()` calls to all 8 silent examples.

**Regression prevention:** Example validation should check that each example produces visible output.

---

## Finding 8: Documentation Version References

**Root cause:** Multiple documentation files contained hardcoded version strings that weren't updated during the v1.1.2 release.

**Why not detected earlier:** No automated documentation version synchronization exists.

**Fix:** Updated all active documentation files to reference v1.1.2.

**Regression prevention:** The release process should include a documentation version audit step.
