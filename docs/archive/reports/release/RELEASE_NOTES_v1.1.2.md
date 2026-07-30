# AILang v1.1.2 Release Notes

**Release Date:** 2026-07-22

## Summary

AILang v1.1.2 is a critical bugfix release addressing verified release blockers identified during independent Release Acceptance Testing. This release focuses on ensuring packaging correctness, version synchronization, and improved diagnostic capabilities. The language design, compiler architecture, and runtime architecture remain frozen, with no new features, refactoring, or performance optimizations introduced.

## Key Improvements & Fixes

### Standard Library Resolution (P0 - MOD003 Fixed)

**Problem:** Previously, when AILang was installed via `pip` and run from an arbitrary directory, it failed to resolve standard library modules (e.g., `json`, `list`, `map`, `string`) with a `MOD003: Module not found` error. This was due to an incorrect path resolution when locating stdlib modules from the installed wheel.

**Solution:** The `_try_discover_stdlib_via_package()` method in `compiler/compilation/session.py` was updated to correctly use `dist.locate_file()`. This ensures that relative paths in the wheel's RECORD file are resolved against the package's installation location, not the current working directory.

**Impact:** Standard library modules now resolve automatically and correctly in all `pip`-installed environments, enabling seamless development and execution of AILang applications.

### Version Synchronization (P1 Fixed)

**Problem:** Inconsistent version reporting was observed, where `pip show ailang-lang` reported `1.1.0` while `ail version` and `pyproject.toml` reported `1.1.1`.

**Solution:** All version sources (`compiler/_version.py`, `pyproject.toml`, CLI output, and package metadata) have been synchronized to `1.1.2`. The wheel was rebuilt to reflect this change.

**Impact:** Ensures a consistent and accurate version across all aspects of the AILang distribution and tooling.

### Doctor Diagnostics Improvement (P1 Fixed)

**Problem:** The `ail doctor` tool incorrectly reported "Standard library: OK" even when the runtime failed to resolve stdlib modules. It also reported "ailang package NOT INSTALLED" despite successful installation from PyPI.

**Solution:** The `check_stdlib_available()` function in `tools/ail_doctor/__main__.py` was enhanced. It now performs a live verification by attempting to resolve key stdlib modules (math, string, list, map, json) using the `ModuleResolver`. The package detection logic was also refined.

**Impact:** `ail doctor` now provides accurate diagnostics, correctly identifying the package installation status and the true resolvability of standard library modules.

## Packaging Improvements

- Ensured correct bundling of all necessary `.ail` files and Python packages within the wheel and source distribution.
- Verified `ail.exe` console script creation and functionality.

## Restrictions Compliance

This release strictly adheres to the established code freeze: no new features, refactoring, performance optimizations, architecture changes, parser/runtime changes, language changes, or breaking API changes have been introduced. All modifications are minimal and targeted solely at resolving the identified release blockers.

## No Breaking Changes

This release contains no breaking changes. Existing AILang code compatible with v1.1.1 will run identically with v1.1.2.

## Important Note for Publishers

This release candidate has been thoroughly verified. Ensure the GitHub Release accurately reflects this version and includes the provided artifacts (wheel and sdist) and these release notes during publication.
