# AILang v1.1.16 (RC1) — Release Candidate Notes

**Release Date:** 2026-08-07
**Release Type:** Release Candidate (patch scope) — pending independent external review
**Status:** Code frozen. **Not published to PyPI or GitHub.** Do not install or distribute externally until an independent reviewer has validated the wheel.

---

## Summary

v1.1.16-RC1 is a maintenance release candidate that fixes the four bugs confirmed during the M134 external review verification milestone and then runs a full release-candidate audit against the packaged wheel. It contains **no language changes, no breaking changes, and no new features**.

The codebase is frozen at v1.1.16. The only remaining step before publishing is a review of the packaged artifacts (`dist/ailang_lang-1.1.16-py3-none-any.whl` and `dist/ailang_lang-1.1.16.tar.gz`) by a completely new, independent reviewer.

---

## Bugs Fixed (M134)

### SEM005 over-reservation narrowed (semantic analyzer)

**Issue:** `_BUILTIN_NAMES` reserved all 70 internal builtin bindings (e.g. `list_copy`, `dict_new`, `__native_to_int`), which are only consumed by `stdlib/*.ail` wrappers. A user function legitimately named `list_copy` was falsely rejected with `SEM005`.

**Fix:** `_BUILTIN_NAMES` is now derived from the `USER_FACING_BUILTINS` set (`frozenset({"print"})`). Internal builtins are pre-declared as module-namespace bindings (non-conflicting with user code). A runtime guard in the interpreter's `_resolve_name` keeps stdlib wrappers resolving internal bindings to the correct builtin even if a user module redefines the same name.

**Regression tests:** internal name reusable, no stdlib hijack, `print` still reserved.

### TYP001 false positive (type checker)

**Issue:** `let new_acc = acc` (recursive-accumulator parameter copy) and `let copy = raw` (copy of a member/call result) were incorrectly flagged `TYP001`.

**Fix:** TYP001 suppression extended from `CallExpressionNode` only to `(CallExpressionNode, IdentifierNode, MemberAccessNode)`. Regression tests added for both cases.

### `ail explain` made ASCII-only (CLI)

**Issue:** `compiler/cli/explain.py` contained stray CJK text and em-dashes, causing mojibake in terminal output.

**Fix:** Explain database is now pure ASCII. Regression test asserts every entry in `ERROR_DATABASE` is ASCII.

### Version consistency

**Issue:** Test assertions, tool fallbacks, the VS Code extension, and docs were pinned to outdated versions.

**Fix:** All surfaces now read the version dynamically from `compiler._version.__version__` or were synced to 1.1.16. `ail doctor` reports "All versions consistent."

---

## Validation

### Full Test Suite

- **1128 tests passed, 0 failed** (87 warnings, 13:18) on a clean post-bump run.
- M134 pre-bump baseline: 1127 passed; affected subsets re-verified at 284 passed; `tests/test_rename.py` at 20 passed.

### Canonical Benchmark

- **5/5 apps OK (15/15 runs), 0 failures** on source after the version bump: dice_roller, hangman_game, inventory_mgmt, kanban, static_analyzer.

### Packaging

- Clean build: `build/` and stale `ailang_lang.egg-info` removed before `python -m build` (build 1.5.1).
- **`twine check` PASSED** for both the wheel and the sdist.
- Packaging audit (`pkg_audit.py`): wheel contains only `ail_platform/`, `compiler/`, `stdlib/`, `tools/`, and `dist-info/`; **banned-pattern scan clean** — no data files, no scratch artifacts (`books.json`, `rtestproj/`, `M133_ENGINEERING_RESPONSE.md`, `.venv`, caches, etc.).
- Wheel installs and imports cleanly in a fresh venv (`.venv_rc1`) with no dependencies beyond the standard library + watchdog.

### Wheel Install Audit (fresh venv, wheel-only)

Every check below was executed **from the installed wheel** (neutral working directory, `PYTHONPATH` empty), not from the source tree:

| Command | Result |
|---------|--------|
| `ail --version` / `ail version` | AILang v1.1.16 |
| `ail doctor` | All versions consistent; no missing required files |
| `ail context --json` | `"version": "1.1.16"` |
| `ail run hello.ail` | `Hello, AILang RC1!`, exit 0 |
| `ail check hello.ail` | "1 file(s) checked, no errors found", exit 0 |
| `ail fmt hello.ail` | exit 0 |
| `ail build hello.ail` | Build successful, exit 0 |
| `ail explain PAR001` | Lists causes |
| `ail docs` | Lists all 6 docs |
| `ail order hello.ail` | No ordering issues found |
| `ail test` (scratch project) | 1/1 passed |
| `ail testgen hello.ail` | **Crashes** with uncaught `ValueError` on wheel install (see Known Limitations — dev-tooling defect, not release-blocking) |
| `ail rename zz_absent zz_new --dry-run` | No references found (guard confirmed off) |
| `ail new demo_proj` | Scaffold created; `ail run demo_proj/main.ail` → exit 0 |
| `ail help` | v1.1.16 usage listing |
| `ail list` | No deps declared (expected) |

**Canonical apps from the wheel:** dice_roller, hangman_game, inventory_mgmt, kanban, static_analyzer (with its required argument) all **exit 0**.

**Not smoke-tested (interactive or network-bound):** `ail watch`, `ail lsp`, `ail mcp`, and the package-manager commands (`install`, `add`, `remove`, `update`, `publish`) — these are long-running servers or registry operations.

---

## Known Limitations (wheel install)

`ail benchmark`, `ail static-analyzer`, and `ail testgen` resolve the app directory relative to the `ail_platform` package location, which under a wheel install is `site-packages/`.

- `ail benchmark` and `ail static-analyzer` report a graceful, actionable error (confirmed by independent review).
- `ail testgen <file>` does **not** degrade gracefully on a wheel install: it crashes with an uncaught `ValueError` traceback (`tools/ail_testgen/generator.py` uses `pathlib.Path.relative_to`, which fails when the target file is not under `site-packages/`). This is a **known defect in the shipped dev tooling**; it does not affect the compiler, runtime, or stdlib, and is not release-blocking.

- Workarounds from a wheel install: `ail run apps/<app>/main.ail`; for benchmark/static-analyzer/testgen, run from a source checkout (`pip install -e .`).

This is a documented wheel limitation, not a regression: all three commands work from the source tree (benchmark 5/5 OK, static-analyzer OK, testgen OK).

**Additional notes from independent review (non-blocking):** under a wheel install, `ail doctor` reports a Repository Health Score of 0/100 (it scans `site-packages` and flags dist-info license files as orphan documents) while still reporting "All versions consistent"; and `ail rename` run outside a project prints the home directory instead of the current working directory in its "no ail.toml found" error. Neither affects the released compiler/runtime/stdlib.

---

## Build Artifacts

| Artifact | SHA256 | Size (bytes) | Built (UTC) |
|----------|--------|-------------:|-------------|
| `dist/ailang_lang-1.1.16-py3-none-any.whl` | `b725211c71951f2df666f0d90826393b334df4bfae27cab5de267ccd2ac46946` | 314,650 | 2026-08-07T14:45:15 |
| `dist/ailang_lang-1.1.16.tar.gz` | `d6b54d159cc895b007ac8784a397377923827807716f8b9a3265dbdf7b5aa4e5` | 417,353 | 2026-08-07T14:45:08 |

---

## What's NOT Changed (freeze statement)

- No language syntax changes
- No breaking changes
- No API changes
- No new features
- No stdlib module changes
- No runtime behavior changes other than the four M134 fixes

The codebase is frozen as of this release candidate. No further changes will be made unless a release-blocking defect is found during external review.

---

## Recommendation

**GO — approved for release after independent review (2026-08-07).**

An independent fresh-context review of the packaged artifacts (wheel + sdist + this document) found **no release-blocking defects** and returned a GO verdict. Every core gate — artifact integrity, wheel contents, CLI behavior, runtime correctness of all five canonical apps, installed stdlib semantics, and sdist installability — was verified directly from the wheel. The single reproducible defect (`ail testgen <file>` crashing on a wheel install) is confined to dev tooling, does not affect the shipped compiler/runtime/stdlib, and is documented above.

Publish steps (paused pending explicit confirmation): tag `v1.1.16`, `twine upload` the wheel + sdist to PyPI, create the GitHub Release. See `RELEASE_CHECKLIST.md` for the process.

---

**Full reference:** `docs/archive/reports/engineering/M134_ENGINEERING_RESPONSE.md` (bug analysis), `CHANGELOG.md` (v1.1.16 entry).
