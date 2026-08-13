# Changelog

## v1.1.18 (M136 Fixes — Published)

**Published:** 2026-08-11 to PyPI and GitHub. Patch release containing the M136
engineering-response fixes. Release gate passed: 1145 tests passing (6
pre-existing failures unchanged from baseline), 55/55 M136 regression tests,
`twine check` PASSED, fresh wheel-only venv verified, canonical 5/5 benchmark
completes from the wheel, post-publication verification from PyPI green. See
`docs/releases/M136_V1_1_18_RC_REPORT.md` and
`docs/archive/reports/engineering/M136_ENGINEERING_RESPONSE.md`.

> **Naming note:** This release contains **M136 J-1..J-5** (below) — **shipped in
> v1.1.18**. It does NOT contain **M136 P0/P1a/P1b** (single-execution `ail run`
> entry + welcome to stderr; `ail testgen` emitting `.ail`; `_frame_ever_bound`
> O(n²)→O(n) name-resolution), which are completed/verified in the working tree
> and pending a future release.

### Bugs Fixed

- **J-1 — `ail rename` crashes under Windows cp1252/piped stdout**: rename
  confirmation messages used the Unicode arrow `→`, which raised
  `UnicodeEncodeError` when stdout was piped on a cp1252 console. Arrow
  replaced with ASCII `->` in `compiler/cli/main.py` and
  `compiler/compilation/session.py`. Regression test:
  `tests/test_rename.py::test_rename_survives_ascii_only_stdout`.
- **J-2 — `ail test` auto-executes `test_*` functions**: test files may now
  define `test_*` functions that are discovered and executed automatically
  (a test fails if its output contains `FAIL`); files that define no
  `test_*` functions fall back to the legacy `main()` convention.
  Implemented via a public `call_function` on the runtime and updated
  `cmd_test` in `compiler/cli/main.py`. Regression tests:
  `tests/test_cli_test_cmd.py` (passing/failing/crashing/multiple/legacy).
- **J-3 — `ail benchmark` streaming/hang fix**: progress lines are now
  flushed immediately (`flush=True`) in `tools/ail_benchmark/__main__.py`
  and `tools/ail_benchmark/runner.py`, with per-benchmark elapsed markers
  and per-run completion markers, so output streams while benchmarks run
  instead of appearing only at process exit. Regression test:
  `tests/test_benchmark_streaming.py`.
- **J-4 — `list.sum` floating-point precision**: summing floats truncated
  to integers. `_coerce_number` in `compiler/runtime/builtins.py` now
  preserves float precision for float and numeric-string values.
- **J-5 — `list.sum_by_key` float/decimal precision and clean errors**:
  `list.sum_by_key` coerces values through `_coerce_number` (floats and
  decimal strings no longer truncate) and raises a deterministic,
  data-focused `RuntimeError` for non-numeric values instead of a generic
  internal error. Regression tests in `tests/test_stdlib_collections.py`.

## v1.1.17 (A100 Community Validation — Published)

**Published:** 2026-08-07 to PyPI and GitHub. Release gate passed: 1217 tests,
5/5 canonical benchmark, `twine check` PASSED, fresh wheel-only venv verified
(8/8 CLI checks), post-publication verification from PyPI green.

Precondition fixes for the A100 Community Validation milestone: wheel-installed
tooling (`ail testgen`, `ail benchmark`, `ail static-analyzer`, `ail doctor`,
`ail rename`) previously resolved the project root relative to the package
location, breaking when installed from a wheel into site-packages (no `apps/`
directory present). See `docs/roadmap/A100_COMMUNITY_VALIDATION.md`.

### Bugs Fixed (A100 Preconditions)

- **`ail testgen <file>` ValueError on wheel installs**: `ail testgen` now
  resolves the project root from the current working directory
  (`resolve_project_root`) and guards against `Relative path ... is not within
  the parent` when the target file lives outside the project tree. Regression
  tests added for single-file and bare-directory invocations.
- **`ail benchmark` / `ail static-analyzer` source-checkout requirement**:
  both tools now fall back to bundled canonical apps packaged inside the wheel
  (`ail_platform/data/apps/`) when no source `apps/` directory exists, and the
  static analyzer runs with its working directory set to the target file's
  parent so runtime sandbox restrictions do not block analysis of files outside
  site-packages.
- **`ail doctor` 0/100 health score on wheel installs**: `ail doctor` now scans
  the user's project (CWD-derived project root) instead of package internals,
  restoring a healthy score on wheel-only installs; package presence checks
  still target the installed package root.
- **`ail rename` wrong directory in error message**: the error now reports the
  actual working directory and includes a hint when a stray project marker
  (`.ail/` directory) exists at a higher level.

### Packaging

- Canonical apps bundled into the wheel under `ail_platform/data/apps/`
  (dice_roller, hangman_game, inventory_mgmt, kanban, static_analyzer).
- `pyproject.toml` package-data and `MANIFEST.in` extended so bundled apps ship
  in both wheel and sdist.

## v1.1.16 (RC1)

Maintenance patch release candidate following the M134 external review
verification milestone. See `docs/releases/RC1_RELEASE_NOTES.md` for the full
audit summary.

### Bugs Fixed (M134)

- **SEM005 over-reservation narrowed**: user code may now define functions
  whose names collide with internal builtin bindings (e.g. `list_copy`); only
  the user-facing `print` builtin remains reserved. A runtime guard keeps
  stdlib wrappers resolving to the correct builtin.
- **TYP001 false positive**: copying a parameter or member/call result
  (`let new_acc = acc`) no longer reports an uninferrable type.
- **`ail explain` made ASCII-only**: removed stray CJK text and em-dashes.
- **Version consistency**: tests, tool fallbacks, VS Code extension, and docs
  synced to the source version.

### Validation (RC1)

- Full test suite: 1127 tests pass.
- Canonical benchmark: 5/5 apps OK.
- Wheel + sdist built and verified from a fresh virtual environment.

## v1.1.15 (M134 External Review Verification & Maintenance)

### Semantic Analyzer

- **SEM005 over-reservation narrowed (external review finding)**: `_BUILTIN_NAMES` previously reserved all 70 internal builtin bindings (`list_copy`, `dict_new`, `__native_to_int`, ...) that are only consumed by `stdlib/*.ail` wrappers. A user function named `list_copy` was falsely rejected with `SEM005`. `_BUILTIN_NAMES` is now derived from the new `USER_FACING_BUILTINS` set (`frozenset({"print"})`); internal builtins are pre-declared as module-namespace bindings (non-conflicting with user code). A runtime guard in the interpreter's `_resolve_name` ensures stdlib wrappers still resolve internal bindings to the builtin even if a user module redefines the same name. Regression tests: internal name reusable, no stdlib hijack, `print` still reserved.

### Type Checker

- **TYP001 false positive fixed (external review finding)**: `let new_acc = acc` (recursive-accumulator parameter copy) and `let copy = raw` (copy of a member/call result) were incorrectly flagged `TYP001`. TYP001 suppression extended from `CallExpressionNode` only to `(CallExpressionNode, IdentifierNode, MemberAccessNode)`. Regression tests added for both cases.

### CLI / DX

- **`ail explain` ASCII-only (external review finding)**: removed stray CJK text and em-dashes from `compiler/cli/explain.py`; the explain database is now pure ASCII. Regression test asserts every entry in `ERROR_DATABASE` is ASCII.

### Version Consistency

- External review found hardcoded `1.1.12`/`1.1.14` assertions in tests and tools. Version asserts in `test_ail_context.py`, `test_mcp_server.py`, `test_vscode_mcp_integration.py` now import `compiler._version.__version__`; `test_v113_regressions.py` uses a tolerant regex. Fallback strings in `tools/ail_context`, `tools/ail_mcp`, `extensions/vscode-ailang/package.json`, `LANGUAGE_SPEC.md`, `PROJECT_MEMORY.md`, `DEVELOPMENT_STATUS.md` synced to `1.1.15`.

### Validation

- Full suite: 1127 tests pass. Canonical benchmark suite: 5/5 apps OK (dice_roller, hangman_game, inventory_mgmt, kanban, static_analyzer).

## v1.1.14 (M132 Maintenance Verification)

### Spec/Implementation Sync

- **Boolean arithmetic (LANGUAGE_SPEC §3.1)**: `true` and `false` now participate in arithmetic expressions (`true + true`, `true + 1`, `true * 2`). Previously the type checker emitted `TYP005` even though the spec, runtime, and stress tests (`test_boolean_in_arithmetic`) all assumed boolean arithmetic works. Type checker now accepts `bool` alongside `int` and `float` for `+ - * / %`, returning `int` when both operands are `bool`/`int` and `float` when either is `float` — matching Python's `bool`⊂`int` semantics.
- **`list.sort` docs fixed**: `docs/releases/V1_RC1_RELEASE_NOTES.md` previously claimed `list.sort(values)` sorts in-place. The implementation, `STDLIB_REFERENCE.md`, and the new `LANGUAGE_SPEC §10.2.1` all state it returns a **new** sorted list (the original is unchanged). Doc fixed to match behavior. New regression tests cover empty input, string sort, no-mutation, and stable sort order.
- **`ail doctor` PyPI fix**: `README.md`, `LICENSE`, and `CHANGELOG.md` are no longer reported as "Missing Required Files" when `ail doctor` runs against a `pip install ailang-lang` site-packages layout (where those files are intentionally absent from the wheel). `is_pypi_install()` detects install mode via the `pyproject.toml` source-tree marker — refined during fresh-release verification because the wheel ships `compiler/`/`tools/`/`stdlib/` into site-packages, so those directories cannot act as source-tree markers.
- **Truthiness spec mirror synced**: The archived `compiler/docs/LANGUAGE_SPEC.md` mirror previously said "The number `0` is truthy", contradicting the canonical spec. Updated to match: "no truthiness coercion in conditions". Regression tests added for `TYP004` (string condition, `if (0)`), `TYP007` (`&&`/`||` with non-bool), and `TYP010` (`!` with non-bool).

### Test Suite

- +22 new M132 regression tests (7 boolean-arithmetic, 4 list.sort, 5 doctor, 6 truthiness coverage).

### Test Summary

| Component | Count |
|-----------|-------|
| Compiler Tests | 1120 |
| Benchmark Tests | 81 |
| **Total Verified** | **1201** |

_(Total verified 1201, up from 1179 in v1.1.13.)_

## v1.1.13

### Evaluation Findings Fixes

- **MOD004 at compile time**: Unknown module member calls (e.g. `math.mod()`, `list.push()`) are now reported during `ail check`/analysis instead of failing silently at runtime. The diagnostic includes the module's available-function list. User modules dropped in favor of same-named stdlib modules are excluded to avoid false positives.
- **CMP001 cascade suppression**: The internal "MissingExpression" compile error is no longer reported when a lexer/parser diagnostic (PAR/LEX) for the same file already explains the failure (e.g. `let x = ;` reports only PAR001).
- **LEX004 non-UTF-8 source**: Source files that are not valid UTF-8 (e.g. UTF-16) now produce a single clean `LEX004` diagnostic with a "re-save as UTF-8" suggestion instead of crashing compilation.
- **Recursion guard**: Default recursion limit is 2000 (matching the v1.1.11 documented default). Python's recursion limit is raised safely above the AILang limit so deep recursion produces a clean structured `Runtime Error` instead of a Python traceback.
- **Runtime error conversion**: `FileNotFoundError`, `PermissionError`, and `UnicodeDecodeError` are converted to structured diagnostics, and error locations prefer the user module over a stdlib file.
- **Sandbox enabled in CLI**: `ail run` now enforces the sandbox by default; the new `--no-sandbox` flag disables it. File access outside the project directory reports a clean sandbox violation with guidance.
- **Version sync**: `ail context`, `ail mcp`, and the VS Code extension now share the canonical `compiler._version` so tool-reported versions cannot drift from `ail --version`.
- **`ail doctor` fixes**: Excludes `.venv_verify`/`generated`/egg-info directories, handles `#anchor` links, resolves relative/directory links (Windows path-separator bug fixed), and the real broken links in current docs were repaired.

**Test Suite**: 1179 tests passing (1098 compiler + 81 benchmarks).

## v1.1.12

### Security & Correctness Hardening

- **Dunder allowlist**: Replaced blocklist with deny-by-default allowlist (`_ALLOWED_DUNDER`) in both `_resolve_name` and `_evaluate_expression`, restricting runtime attribute access to safe data-model dunders.
- **Builtin shadowing protection**: New `SEM005_BUILTIN_SHADOW` error code in semantic analyzer prevents declarations that shadow built-in names (`print`, `list_*`, etc.) at compile time.
- **Regression tests updated**: `test_shadow_builtin` updated to expect compile-time diagnostic instead of runtime shadowing.
- **Audit closure item**: Remaining compiler hardening improvements from the audit findings complete.

**Test Suite**: 1088 tests passing.
**Publication**: Published to PyPI and GitHub Releases.

## v1.1.11

### Production Readiness — Audit Findings Sprint

Six audit-priority improvements for compiler and runtime stability:

- **Recursion guard**: `_call_depth` counter in `Runtime` with `sys.setrecursionlimit(max_depth + 5000)`. Default max depth = 2000 from sandbox policy.
- **Python exception isolation**: User-facing `NameError`, `TypeError`, `AttributeError` converted to structured `RuntimeError`. Top-level `execute()` catch-all wrapper.
- **`parse_identifier` fix**: Returns `MissingExpression` node on failure instead of broken `Identifier` with no token.
- **`MissingExpression` detection**: `_build_MissingExpression` raises `ValueError` instead of silently filtering.
- **IR validator wired**: `IRValidator.validate(ir)` called inside `CompilationSession.build_ir()` for every module.
- **Fuzz test harness**: 4 tests (100 random programs, 50 random byte streams, deeply nested expressions at depth 200, deep recursion chains at 800 calls). All pass.

**Test Suite**: 1088 tests passing.
**Publication**: Published to PyPI and GitHub Releases.

## v1.1.10

### Maintenance Release — Project Template Version Fix

- **Fixed**: `ail new` project template now generates `ail.toml` with correct language version (`1.1.9` instead of stale `1.1.7`).

**Impact**: No language, compiler, or runtime changes. Fully backward compatible with v1.1.9.

## v1.1.9

### M129 Engineering Response — Independent Validation First Iteration

This patch release addresses all accepted findings from the M128 independent validation of the v1.1.8 release. v1.1.8 remains published and immutable.

- **High Priority Fixes**:
  - `ail order` output path: Changed `get_project_root()` to `Path.cwd()` so outputs write to the working directory, not site-packages (`tools/ail_order/__main__.py:114`).
  - LANGUAGE_SPEC default parameters: Removed §5.1 reference to unimplemented default parameter feature — all parameters are required, matching LANGUAGE_TOUR (both copies: `compiler/docs/`, `docs/reference/`).
  - Division-by-zero runtime error: `interpreter.py` `/` and `%` ops now catch `ZeroDivisionError` → structured `RuntimeError` with operation/reason/expected/actual/location/suggestion.
  - List index out-of-range: `builtins.py` `list_get` now catches `IndexError` → structured `RuntimeError` with index, length, bounds suggestion.
  - Broken link fixes: GETTING_STARTED (`COMPILER_ARCHITECTURE.md` → `LANGUAGE_SPEC.md`), LANGUAGE_TOUR (`../LANGUAGE_SPEC.md` → `LANGUAGE_SPEC.md`).
- **Version Synchronisation**:
  - Updated LANGUAGE_SPEC and language tool versions to v1.1.9 across 10 files: `compiler/docs/LANGUAGE_SPEC.md`, `docs/reference/LANGUAGE_SPEC.md`, `tools/ail_context/__main__.py`, `tools/ail_mcp/*.py` (3), `tools/ail_package_manager/init.py`, `tools/ail_package_manager/manifest.py`, `extensions/vscode-ailang/package.json`.
  - Updated all test version assertions and development status references.
- **Documentation**:
  - README: Added note that CLI is `ail` (not `ailang`).
  - `ail testgen`: Usage help now shows `--app APP` flag.
- **Test Suite**: 1084 tests passing (full suite).
- **Publication**: Published to PyPI and GitHub Releases.

## v1.1.8

### M127 P0 — Runtime Diagnostics & Package Validation (Final Release)

This release is the final v1.1.8, incorporating the RC Technical Review fixes.

- **RC Technical Review Fixes**:
  - `compiler/runtime/interpreter.py:285` — removed line that concatenated line number into `source_file` in fallback path (double-line-number bug).
  - `compiler/runtime/builtins.py:243-246` — replaced `cast(list, args[0])` with `_expect_list(args[0], "list.clear")` in `list_clear`.
- **Publication**: Published to PyPI and GitHub Releases.
- **Test Suite**: 1165 tests passing.

## v1.1.7

### Developer Experience (DX) Improvement Sprint — M121/M122 Release Candidate

This release implements all Developer Experience remediation findings from the independent Developer 4 application build evaluation (M120).

- **Tooling Fixes**:
  - `ail doctor`: Fixed indefinite hanging by introducing file scan limits (max 5000 files), 10-second per-check timeouts, and expanded directory exclusions (`reports/`, `generated/`, `.pytest_cache`, etc.).
  - `ail docs`: Added `GETTING_STARTED`, `LANGUAGE_TOUR`, and `VSCODE_QUICKSTART` to the offline document retrieval registry. Bundled all reference documentation into `compiler/docs/`.
  - `ail explain`: Populated the explanation database (`compiler/cli/explain.py`) for all 11 previously missing error codes (`PAR001-003`, `LEX001-003`, `TYP011-013`, `MOD002`, `SEM004`, `CMP001`, `LSP000`), including broken/fixed examples and return expression guidance.
- **Specification & Documentation Parity**:
  - Synchronized `LANGUAGE_SPEC.md` §11.1 and Appendix E with the runtime error registry (`compiler/diagnostics.py`), adding 13 missing runtime codes and removing obsolete `MOD005`.
  - Added full documentation and code examples for `io.read()` in `STDLIB_REFERENCE.md`.
  - Added a dedicated "Design Philosophy and Constraints" section to `GETTING_STARTED.md` explaining the architectural rationale for recursion-only iteration, mandatory return expressions, and map/list primitive data structures.
- **Packaging & Distribution**:
  - Added proper `__init__.py` files for `tools/` submodules.
  - Updated `pyproject.toml` package data to ensure all documentation files are bundled in wheels and source distributions.
- **Test Suite**:
  - All tests passing successfully.

### M127 P0 — Runtime Diagnostics & Package Validation (Release Candidate)

This milestone implements structured, deterministic error messages across the runtime and package management systems, plus wheel packaging verification. v1.1.7 is a release candidate — not yet published to PyPI or GitHub Releases.

- **Runtime Diagnostics** (`compiler/runtime/errors.py`):
  - New `RuntimeError` exception class with `format_diagnostic()` — structured output: operation, reason, expected type, actual type, source location, suggestion.
  - 30+ stdlib type validation guards in `compiler/runtime/builtins.py` (`_expect_list`, `_expect_dict`, `_expect_set`).
  - Source span tracking and `_augment_error()` in `compiler/runtime/interpreter.py`.
  - `CallIR` wraps builtin calls in try/except for clean error capture.
  - `cmd_run` / `cmd_test` in `compiler/cli/main.py` build source map and render `RuntimeError` diagnostics (no Python tracebacks shown).
- **Package Validation** (`tools/ail_package_manager/errors.py`):
  - New `PackageError` exception class with `format_diagnostic()` — deterministic output: reason, suggestion, detail, manifest_path, location.
  - Structured diagnostics across manifest validation, installer, commands, init, cache, resolver.
  - Entry file validation is a **warning** not a hard error.
- **Exit Codes** (`ail_platform/report_schema.py`):
  - Replaced generic `INTERNAL_ERROR` with specific codes: `MANIFEST_NOT_FOUND=10`, `INVALID_PACKAGE_NAME=11`, `INVALID_VERSION=12`, `INVALID_ENTRY=13`, `INVALID_DEPENDENCY=14`.
- **Documentation**:
  - New `docs/guides/PACKAGE_VALIDATION.md` — validation lifecycle, diagnostic examples, troubleshooting.
  - Map iteration patterns added to `STDLIB_REFERENCE.md` — common usage, mistakes (`list.get` on maps, unguarded `map.get`), cross-references to runtime diagnostics.
  - README updated: CLI command reference table, troubleshooting section, test count badges (1136→1165).
- **Wheel Packaging Verification**:
  - `ailang_lang-1.1.7-py3-none-any.whl` built and installed into clean venv.
  - Verified: `ail --version` = v1.1.7, `ail --help` shows all commands, `pip show ailang-lang` metadata correct.
  - Verified: hello_world, calculator, collections, fibonacci all execute correctly.
  - Verification report archived.
- **Test Suite**: 48 existing package tests + 29 new validation tests + 87 runtime/CLI/diagnostic = 164 new/updated tests. Total: 1165 tests passing.
- **Binaries**: `compiler/runtime/errors.py`, `tools/ail_package_manager/errors.py` (new), `docs/guides/PACKAGE_VALIDATION.md` (new), `tests/test_package_validation.py` (new).
- **No language, grammar, parser, AST, or semantics changes.**

### No Changes

- No language changes
- No breaking changes
- No API changes
- Runtime interpreter frozen

## v1.1.6

### Remediation Sprint — M106 Post-Release Audit Fixes

This release addresses all issues identified in the independent M106 post-release audit.

- **Critical Bug Fixes**:
  - Fixed compiler crash (`AssertionError`) when single quotes are used in function call arguments (`compiler/ast/builder.py`).
  - Fixed `ail rename` crash (`NameError: name 'RenameTool' is not defined`) — restored missing import (`compiler/cli/main.py`).
- **High Severity Fixes**:
  - Fixed `ail doctor` misreporting package as NOT INSTALLED when installed from PyPI (`tools/ail_doctor/__main__.py`).
  - Fixed Unicode encoding bug in `ail docs` — em dash no longer replaced with "???" (`tools/ail_docs/__main__.py`, `compiler/cli/main.py`).
  - Fixed LEX002 cascade suppression — unterminated strings now produce 1 diagnostic instead of 3 (`compiler/diagnostics.py`, `compiler/compilation/session.py`).
- **Diagnostics Improvements**:
  - Fixed duplicate diagnostic reporting — `DiagnosticReporter` now deduplicates exact matches (`compiler/diagnostics.py`).
  - Updated `ail context` diagnostic codes to match the actual compiler (`tools/ail_context/__main__.py`).
- **CLI Consistency**:
  - `ail doctor --help` and `ail explain --help` now display proper help text (`compiler/cli/main.py`).
- **Documentation Synchronization**:
  - Corrected README.md badge and text to show 1136 passing tests.
  - Updated `CHANGELOG.md` test count (1047 → 1136).
  - Updated `ail.toml` template language version from "0.3" to "1.1.5" (`compiler/cli/main.py`, `tools/ail_package_manager/init.py`).
  - Added `string.concat` arity documentation to STDLIB_REFERENCE.md.
- **Test Suite**:
  - Fixed 5 stale test assertions checking for v1.1.4 instead of v1.1.5.
  - All 1136 tests are passing.
- **Tooling Fixes**:
  - Fixed static-analyzer output path — now writes to current working directory instead of package directory (`tools/ail_static_analyzer/__main__.py`).

### No Changes

- No language changes
- No breaking changes
- No new features
- No API changes

## v1.1.5

### Production Release — Independent Certification Complete

This release incorporates critical production readiness fixes and passes independent certification. AILang v1.1.5 is now PRODUCTION READY.

- **Security Hardening**:
  - Implemented comprehensive runtime sandboxing for file I/O, environment access, and recursion limits (`compiler/runtime/sandbox.py`).
  - Patched Zip Slip vulnerability in `tarfile.extractall()` across package management tools.
  - Blocked dangerous dunder attribute access in the interpreter (`__class__`, `__subclasses__`, etc.) to prevent sandbox escapes.
- **Diagnostics Completion**:
  - All 37 compiler error codes now have named constants and detailed explanations (`compiler/diagnostics.py`).
  - Removed obsolete diagnostic code (`MOD005`).
- **CLI Usability Improvements**:
  - All 27 CLI commands now consistently support the `--help` flag, providing clear usage information.
  - `ail lsp --help` now displays help instead of starting the server.
- **Documentation Synchronization**:
  - Corrected README.md test counts (1136 passing).
  - Updated AGENTS.md with accurate claims regarding stdlib functions (`list.sort`, `list.copy`) and loop rules.
  - Ensured version consistency across `LANGUAGE_SPEC.md`, `README.md`, and internal tool versions.
- **Packaging Improvements**:
  - VS Code extension version bumped to 1.1.5.
  - Synchronized compiler and tool versions across the repository.
  - `.gitignore` updated to exclude profiler outputs and generated project context files.
- **Test Suite**:
  - All 1136 tests are passing, including new security regression tests.
  - Resolved minor version mismatch issues in test assertions.

### No Changes

- No language changes
- No breaking changes
- No new features
- No API changes

## v1.1.4

### Bug Fix — Stdlib Module Resolution (MOD003)

- **Fixed MOD003: stdlib module resolution from outside project tree**. Programs importing stdlib modules (`string`, `math`, `list`, `map`, `json`, etc.) can now be compiled and run from any directory, not just from within the project tree. Previously, running from a temp directory or other location outside the repo would fail with `ERROR MOD003: Module not found`.
- **Root cause**: `ModuleResolver._candidate_roots()` did not include the installed package's stdlib directory as a fallback search path.
- **Fix**: Added `_find_stdlib_root()` helper to `compiler/compilation/resolution.py` and updated `_candidate_roots()` to include installed stdlib as a fallback.
- **New regression test**: `tests/test_mod003_stdlib_resolution.py` permanently protects against this issue.

### No Changes

- No language changes
- No breaking changes
- No API changes
- No new features

### Tests

- 4 new integration tests protecting against MOD003 regression
- All 1018 tests pass

## v1.1.3

### M92 — Release Polish & New Developer Tools

- **5 new development tools added**:
  - `ail_doc_verify`: Documentation verification
  - `ail_dx_audit`: Developer experience audit
  - `ail_release_verify`: Release verification
  - `ail_stdlib_audit`: Standard library audit
  - `ail_validate`: Validation pipeline runner
- **Examples remediated**: All 50+ examples verified with consistent formatting and output
- **Validation pipeline**: New `validation_pipeline.json` for automated quality gates
- **Documentation cleanup**: Version references synchronized, stale links fixed
- **AI Developer Guide**: New comprehensive guide for AI-assisted development

### Tests

- Test assertions updated for version 1.1.3
- All existing tests continue to pass

## v1.1.2

### M91 — Release Engineering Recovery

- **Version synchronization**: All version references now consistently show v1.1.2 (pyproject.toml, compiler/_version.py, tools, README badge)
- **Release automation**: Integrated generate_version.py into the release workflow
- **Automated verification**: Release pipeline verifies version consistency before building

### M89 — External Validation Remediation (from v1.1.1 release)

- **Version synchronization**: All public version references now consistently show v1.1.2 (README, CHANGELOG, CLI, ail.toml, package metadata)
- **Template repair**: Generated `main.ail` now includes semicolon on `return` statement; ail.toml language version updated to match package version
- **Official examples remediated**: 3 member_access examples verified working with dot syntax; recursive_map renamed to avoid stdlib name collision
- **Showcase applications remediated**: hotel_management and kanban renamed functions colliding with stdlib builtins (`list_find_by_key`, `list_filter_by_key`, `list_filter_by_contains`, `list_copy`)
- **CLI help consistency**: Core commands (`run`, `build`, `fmt`, `test`, `new`, `check`, `rename`, `watch`) now support `--help` flag with consistent exit code 0
- **Silent examples improved**: 5 examples that produced no output now include `print()` calls demonstrating their behavior
- **Documentation synchronized**: Member access examples verified, version references updated across all documentation

### Tests

- All existing tests continue to pass (1079+)
- Regression tests added for template output, example compilation, and CLI help behavior

## v1.1.1

### M83I — Enterprise Validation Fixes

- **`ail rename` project root detection**: Fixed `ail rename` to detect the user's project root by walking CWD upward for `ail.toml` or `.ail` markers, instead of using the AILang package's stdlib parent. Renaming now correctly scans the user's project files.
- **Unknown flag handling**: `ail --invalid-flag` now reports `Error: unknown option '--invalid-flag'` with a general usage hint, instead of dispatching to `cmd_run` which showed the run-specific usage.
- **SEM001 diagnostic location consistency**: Pre-registration of module exports now sets `file_path` and source text on the symbol table, so duplicate declaration errors always include the source file path.
- **LEX002 cascade suppression**: Unterminated string errors (LEX002) now suppress downstream parser cascade errors (PAR001), reducing diagnostic noise from 7+ errors to 1.
- **SEM003/TYP011 deduplication**: The type checker now skips TYP011 (arity mismatch) when SEM003 (semantic arity check) already reported the same error, eliminating confusing dual error codes.
- **Suggested fixes for LEX002 and SEM001**: Added actionable next-step suggestions ("Add a closing quote..." for LEX002, "Rename one of the duplicate declarations..." for SEM001).
- **MOD003 module-not-found diagnostic**: Import resolution failures now emit MOD003 (Module not found) instead of silently falling through to MOD004 (Symbol not found in module).

### Tests

- 16 new regression tests covering all 7 fixes (test_m83i_fixes.py)

## v1.1.0

### M77.1 — Local Package Management MVP

- **Lock file format update**: `ail.lock` now uses `[[package]]` (singular), `resolved_version` instead of `version`, and `commit` field for git dependencies
- **Git+ URL shorthand**: Manifest now supports `audit = "git+https://..."` string format alongside the existing table syntax
- **Version conflict detection**: Resolver now detects and reports version conflicts with actionable diagnostics showing conflicting constraints
- **Improved circular dependency detection**: Circular dependencies are now detected even when the cycle involves already-visited packages, with clear cycle path in error message
- **`--verbose` flag**: `ail install --verbose` (or `-v`) shows manifest path, project root, lib/cache dirs, dependency details, and per-package install steps
- **`--frozen` alias**: `ail install --frozen` is now a shortcut for `--frozen-lockfile`
- **Lockfile staleness exit code**: `--frozen-lockfile` now returns exit code 4 (LOCKFILE_MISMATCH) instead of generic FAILURE when the lockfile is stale
- **Package-specific exit codes**: Added `RESOLUTION_FAILURE=1`, `CIRCULAR_DEPENDENCY=2`, `INVALID_MANIFEST=3`, `LOCKFILE_MISMATCH=4`, `GIT_CLONE_FAILURE=5` to `ExitCode`
- **Lockfile input hash comment**: Updated comment to clarify hash is of `ail.toml`

### Tests

- 16 new tests covering local deps install, lockfile format, reproducible installs, circular detection, verbose output, frozen lockfile, and exit codes

## v1.0.10

### M76.2A — NumericUnknownType for Unknown+Unknown Arithmetic

- **NumericUnknownType**: Introduced separate frozen dataclass (not a subclass of UnknownType) to represent Unknown+Unknown arithmetic results without silent incorrect inference
  - `UnknownType + UnknownType → NumericUnknownType` (not directly INT_TYPE, avoiding false positives when values are strings)
  - Runtime validation unchanged: `NumericUnknownType` values are still dynamically typed at runtime
- **Type checker arithmetic block**: Updated all `isinstance` checks to handle `NumericUnknownType` via `_num_unk` lambda for proper inference
- **Type checker comparison/assignment/return/member-access blocks**: Updated to suppress TYP003, TYP006, TYP008, TYP009 for `NumericUnknownType`
- **Type checker logical operators**: `NumericUnknownType` intentionally triggers TYP004/TYP007/TYP010 as errors (logical ops on numeric unknown is invalid)
- **Regression tests**: 5 new tests covering Unknown+Unknown, Unknown*Unknown, unknown functions, accumulator patterns, and Unknown-Unknown

### M76.2B — ail check Semantic Analysis

- **ail check rewrite**: Now runs full compilation pipeline (forward-reference check → semantic analysis → type checking) instead of only forward-reference checks
- **Session type_check fix**: `type_check()` now pre-declares user functions in the fresh SymbolTable so the type checker can resolve cross-function calls and detect TYP003
- **CLI integration**: `ail check` and `ail build` now report identical diagnostics
- **Integration test**: Added `test_ail_check_detects_type_error` verifying `ail check` fails on TYP003

## v1.0.11

### M76.3A — Type Flow Propagation

- **Function return type inference**: Type checker now correctly infers return types from `return` statements inside function bodies, enabling type flow through function calls (e.g., `let x = get_val(); let y = x + 1` infers `x` as `INT_TYPE` if `get_val()` returns `42`)
- **Chained function calls**: Type propagation works through multiple function call layers (e.g., `get_a() + get_b()` infers `INT_TYPE`)

### M76.3B — Better TYP001 Diagnostics

- **TYP001 enriched messages**: Error now shows the expression that caused the inference failure, along with specific suggestions (e.g., "Use explicit conversion helpers", "Initialize values using typed literals")
- **Related commands**: TYP001 output now suggests `ail explain TYP001`, `ail heal`, and related commands
- **Helpers**: Added `_format_expression()` and `_build_typ001_message()` to `TypeChecker`

### M76.3C — `ail explain` Command

- **New `ail explain <CODE>` command**: Shows detailed explanation of error codes including common causes, broken/fixed examples, fixes, related commands, and `ail heal` suggestions
- **Full error code database**: 17 error codes documented (TYP001–TYP010, SEM001–SEM003, MOD001/MOD003/MOD004)
- **No-args behavior**: `ail explain` lists all known error codes with one-line descriptions
- **Unknown code handling**: Clear error message for unrecognized codes

### Tests

- 10 new tests covering type flow propagation, TYP001 diagnostic enrichment, and `ail explain` command

## v1.0.9

### M76.1 — Arithmetic Inference Improvements

- **Arithmetic with UnknownType**: Type checker now infers numeric types in arithmetic operations when one operand is UnknownType
  - `UnknownType + INT_TYPE` → `INT_TYPE` (enables `map.get(m, "qty") + 1`)
  - `INT_TYPE + UnknownType` → `INT_TYPE`
  - `UnknownType - INT_TYPE` → `INT_TYPE`
  - `INT_TYPE - UnknownType` → `INT_TYPE`
  - `UnknownType * INT_TYPE` → `INT_TYPE`
  - `INT_TYPE * UnknownType` → `INT_TYPE`
  - `UnknownType / INT_TYPE` → `FLOAT_TYPE`
  - `INT_TYPE / UnknownType` → `FLOAT_TYPE`
  - `UnknownType % INT_TYPE` → `INT_TYPE`
  - `INT_TYPE % UnknownType` → `INT_TYPE`
  - Same support for FLOAT_TYPE operands
- **Source-diverse UnknownType support**: Arithmetic inference works with UnknownType from any source (map.get, json.parse, unknown functions, module functions)
- **Regression tests**: Added 7 new tests covering all arithmetic operator combinations with UnknownType

## v1.0.8

### M75.4 — Developer Experience & Discoverability

- **Context-aware diagnostics**: Error output now shows specific next-step commands (e.g., `ail heal`, `ail docs AGENTS.md`)
- **First-run experience**: New users see a welcome guide on first `ail` invocation, persisted to `~/.ail/state.json`
- **`ail heal` tool**: New command providing fix suggestions for forward references, type errors, missing imports, import aliases, operator errors, loops, and environment setup
- **Improved `ail doctor`**: Added checks for Python version, stdlib availability, docs, MCP server, LSP server, PATH, VS Code extension, and ailang package
- **Enhanced `ail --help`**: Added "New to AILang?" onboarding section with recommended workflow
- **Workflow metadata**: `ail context --json` and MCP `get_language_context` now include `recommended_workflows` and `dx_tools` metadata for AI-guided development
- **Improved diagnostics**: `Diagnostic` dataclass now includes `next_steps` field; `DiagnosticFormatter` provides `format_summary()` and `suggest_next_steps()` methods
- **Tests**: 27 new tests for diagnostics, context, heal, first-run, doctor, and path-leakage prevention

### M75.5 — Remove Local Path Leakage

- **Path leakage audit**: Systematic scan of entire repository for absolute paths, developer-specific filesystem references, and internal structure hints
- **Fixed `ail doctor`**: Now prints to stdout instead of writing to `generated/DOCTOR_REPORT.md`; removed path disclosure from `ail CLI` check
- **Fixed `ail context`**: Now prints to stdout by default; `--output` flag available for explicit file writes
- **Added `retrieval_policy`**: Both `ail context --json` and MCP `get_language_context` now include explicit policy declaring allowed/forbidden retrieval methods
- **Sanitized benchmark metadata**: Replaced all absolute paths with relative paths in `benchmarks/datasets/`
- **Sanitized reports**: Replaced absolute paths with relative paths in `reports/DEPENDENCY_ORDERING_REPORT.md` and `reports/dependency_ordering.md`
- **Sanitized docs**: Cleaned absolute paths from `docs/research/M63_FALSE_POSITIVE_ANALYSIS.md` and `docs/releases/M63_AIL_CHECK_REPORT.md`
- **Cleaned profile data**: Sanitized `tools/python_profile_data.json` (65+ absolute path entries)
- **Cleaned rename manifests**: Sanitized `.ail/rename/` manifest files
- **Path-leak-free tests**: 6 new tests verifying no local paths leak through `ail context`, `ail doctor`, `ail heal`, or benchmark metadata

## v1.0.7

### M75.3 — Type Inference & Discoverability

- **String concatenation with UnknownType**: Fixed type checker to allow `STRING_TYPE + UnknownType → STRING_TYPE` (was erroring with TYP005)
- **Import alias runtime support**: `import module as alias` now works at runtime — aliases are registered in the interpreter and resolved during execution
- **Unicode encoding fix**: `ail docs` now handles Unicode characters on Windows (reconfigure stdout to UTF-8)
- **Discoverability improvements**: Updated README with Core Commands section, Language Tour with import alias example, and `io.read` in stdlib table
- **Documentation**: Updated LANGUAGE_SPEC, STDLIB_REFERENCE, DEVELOPMENT_STATUS, PROJECT_MEMORY with v1.0.7 features

## v1.0.6

### M75.2 — Validator-Driven Polish

- **Boolean type inference**: Fixed return/param types to use `UnknownType()` instead of `INT_TYPE` for better inference
- **`io.read()` builtin**: Added stdin reading capability to the `io` module
- **SEM002 diagnostics**: Improved error messages for undefined identifiers
- **MCP Server tool**: Added `get_document` tool for document retrieval
- **Tests**: Updated type checker, MCP, and VS Code integration tests

## v1.0.5

### M72 — VS Code Extension with MCP Integration

- **VS Code Extension v0.3.0**: Full language support with LSP + MCP dual-server architecture
- **LSP Server**: 14 methods — diagnostics, hover, completion, go-to-definition, find references, rename, signature help, symbols, code actions
- **MCP Client**: JSON-RPC 2.0 over NDJSON transport with automatic server lifecycle management
- **7 Commands**: Start/Stop/Restart MCP Server, Compile, Explain, Insert Example, Show Status
- **Status Bar**: Real-time MCP server state indicator
- **5 Configuration Settings**: Auto-start, command, args, timeout, max reconnect attempts
- **Tests**: 26 new VS Code MCP integration tests, all passing

### M73 — Reference Applications & AI Training Corpus

- **8 Reference Applications** under `apps/reference/`:
  - `todo_manager` — list CRUD, map operations, JSON persistence (~97 LOC)
  - `expense_tracker` — aggregation, category filtering, CSV export (~145 LOC)
  - `inventory_lite` — map CRUD, stock operations, JSON persistence (~120 LOC)
  - `employee_management` — filtering, salary reports, CSV export (~142 LOC)
  - `log_analyzer` — file parsing, string splitting, level counting (~137 LOC)
  - `csv_etl` — CSV parsing, validation, transformation pipeline (~104 LOC)
  - `json_transformer` — JSON normalization, string operations (~81 LOC)
  - `invoice_generator` — business logic, tax calculation, JSON export (~110 LOC)
- **AI Usage Documentation**: Each app includes `AI_USAGE.md` documenting AI-assisted development patterns
- **MCP Examples**: 12 categories available via `get_examples` tool (6 original + 8 reference apps)
- **Documentation**: `docs/reference/REFERENCE_APPLICATIONS.md`

## v1.0.4

### M71 — MCP Server + AI Toolchain Integration

- **MCP Server**: `ail mcp` command starts a Model Context Protocol server on stdio transport
- **5 MCP Tools**:
  - `get_language_context` — returns language rules, workflow, diagnostics (equivalent to `ail context --json`)
  - `get_stdlib` — returns standard library modules, functions, and signatures
  - `compile_source` — compiles AILang source code and returns diagnostics
  - `explain_diagnostic` — returns detailed explanation for diagnostic codes with examples
  - `get_examples` — returns canonical AILang code examples
- **JSON-RPC 2.0** — standard MCP protocol over stdio transport
- **AI tool integration** — works with Claude Code, Cursor, and custom MCP clients
- **Documentation**: `docs/architecture/MCP_SERVER.md`, `docs/reference/MCP_QUICKSTART.md`
- **Tests**: 14 new MCP tests, all passing

### AI Documentation Stack

- **`ail context --json`** — machine-readable language manifest (v1.0.3)
- **AGENTS.md in wheel** — AI agents find documentation after `pip install`
- **README.md** — AI Agent Setup section with document hierarchy
- **AGENTS.md** — "derived from LANGUAGE_SPEC.md" disclaimer

## v1.0.3

### Type Checker Hardening (M69.7 completion)

- **Shared symbol table**: Type checker now receives builtins and module namespace declarations from the semantic analysis phase, eliminating false SEM002 "Undefined identifier" errors for stdlib and imported module calls
- **TYP013 false-positive suppression**: Calling a function whose type is unknown (e.g., stdlib, imported, or unannotated functions) no longer emits "Cannot call non-function type unknown" — only known non-function types (e.g., `42()`, `"hello"()`) trigger TYP013
- **UnknownType cascade suppression**: TYP003/TYP004/TYP005/TYP006/TYP007/TYP008/TYP009/TYP010 errors are suppressed when operand types are unknown, preventing cascading false positives from unresolvable identifiers
- **TYP012 arg-count guard**: Argument type mismatch (TYP012) is suppressed when all parameter types are the hardcoded INT_TYPE default, since the type checker lacks parameter type inference
- **TYP008 assignment guard**: Assignment type mismatch (TYP008) is suppressed when the right-hand side has the hardcoded INT_TYPE return default
- **String concatenation**: `+` operator with STRING operands returns STRING (matches runtime behavior)
- **Variable declaration fallback**: Type checker declares variables/functions not found in its symbol table instead of emitting SEM002

### Pre-existing Bug Fixes

- **CLI no-args exit code**: `ail` with no arguments now returns exit code 1 (error) instead of 0, consistent with CLI conventions and all subcommands
- **IR crash test rewrite**: `test_for_loop_multiple_accumulators` rewritten to use valid AILang syntax and correct multi-accumulator pattern

### Test Results

- 931 collected, 931 passed, 0 failed
- All 5 verification checks pass: TYP013 preservation, stdlib compilation, imported module compilation, exported module compilation, no new false negatives

## v1.0.0-M57

### M57 — VS Code Extension Hardening

- **Extension version sync**: Bumped `package.json` to v0.2.0; fixed trailing comma; added icon reference
- **Code action edits**: Rewrote `compiler/lsp/features/code_actions.py` — quick fixes now generate actual `TextEdit` operations for "import stdlib module" and "remove unused variable" actions
- **`for` keyword support**: Added to TextMate grammar (`keyword.control.loop.ailang`) and LSP completions (`completion.py`)
- **Documentation**: `docs/vscode/INSTALLATION.md` (installation guide), `docs/vscode/FEATURES.md` (feature reference), `docs/releases/M57_VSCODE_EXTENSION_REPORT.md`
- **Extension CHANGELOG**: Updated `extensions/vscode-ailang/CHANGELOG.md` with v0.2.0 entry
- **Test results**: 103/103 LSP tests passing, zero regressions

## v1.0.0-M56

### M56 — External Adoption Closure (Package Naming + Package Manager Commands)

- **Snake-case package naming**: Resolved naming deadlock — `manifest.py` now accepts `^[a-z][a-z0-9_]*$` (snake_case). Kebab-case accepted with deprecation warning for backward compatibility
- **Resolver normalization**: `compiler/compilation/resolution.py` tries both kebab-to-underscore and underscore-to-kebab variants when resolving package directories in `lib/`
- **`ail new` generates `ail.toml`**: Previously only created `main.ail` + README; now creates `ail.toml` and `ail.lock` with snake_case-normalized package name
- **`ail add`**: Implemented in `tools/ail_package_manager/commands.py` — parses `name@version`, `--path`, `--git`/`--tag`/`--branch`; edits `ail.toml` [dependencies] section
- **`ail remove`**: Removes dependency lines from `ail.toml` by matching `"<name>"` prefix
- **`ail update`**: Delegates to `tools.ail_package_manager.installer.install()` for re-resolution
- **`ail list`**: Reads `ail.toml` dependencies and `lib/` directory to show install status
- **CLI wiring**: All four commands added to `compiler/cli/main.py` dispatch table, help text, and `tools/ail_package_manager/__main__.py` argparse
- **Documentation**: `docs/PACKAGE_NAMING_POLICY.md`, `docs/QUICKSTART.md`, `docs/PACKAGES.md`, `docs/research/M56_EXTERNAL_ADOPTION_CLOSURE.md`
- **Test results**: 32 new tests (19 naming + 13 commands), all passing. Total: 176/176 tests across LSP + naming + commands + CLI

## 0.10.0

### DX-015 — Repository Rename Tool (`ail rename`)

- **`ail rename old_name new_name`**: Repository-wide identifier rename with semantic awareness
- **Symbol graph scanning**: Parses all `.ail` files via the compiler pipeline to find function declarations, function calls, variable declarations, variable references, parameters, and import path segments matching the old name
- **`--dry-run`**: Preview changes without modifying files
- **`--diff`**: Show unified diff of all changes
- **`--strings`**: Also rename matching string literal values (e.g., map keys)
- **`--no-verify`**: Skip compiler verification after rename
- **Atomic file rewriting**: Changes applied from end to start to preserve offsets; temporary `.rename.tmp` file used per file
- **Rollback bundle**: Every rename creates `.ail/rename/<timestamp>/` with a `manifest.json` and `.orig` backups of every modified file; on failure, all files are automatically restored
- **Compiler verification**: After successful rename, `ail build` runs on the entry point to detect any compilation errors
- **Safe identifier validation**: `new_name` must pass `str.isidentifier()` to prevent invalid identifiers
- **Implementation**: `compiler/rename.py` — ~260 LOC, no modifications to compiler pipeline, parser, or runtime

### DX-016 — Watch Mode (`ail watch`)

- **`ail watch [<entry>]`**: Automatic incremental recompilation on file changes
- **Filesystem watcher**: Uses `watchdog` library for cross-platform file monitoring (Windows `ReadDirectoryChangesW`, macOS `FSEvents`, Linux `inotify`)
- **`--poll`**: Polling-mode fallback for network filesystems, Docker, WSL
- **`--json`**: Machine-readable JSON output for AI tooling integration
- **`--no-initial`**: Skip the initial full build on startup
- **Incremental compilation**: `CompilationSession.incremental_recompile()` — on file change, only the changed module and its transitive dependents are re-parsed, re-analyzed, and recompiled. Unchanged modules use their existing ASTs
- **Dependency invalidation**: `get_transitive_dependents()` computes the full affected set via BFS on the import graph
- **Cross-module semantic reanalysis**: Only affected modules are deep-analyzed; cross-module export registration for all modules is fast (top-level names only)
- **SHA-256 change detection**: `FileCache` stores per-file hashes; events that don't change content (editor atomic-save artifacts) are filtered out
- **Debounce (200ms)**: Threading.Timer-based debounce prevents redundant compiles during AI burst edits
- **Polling fallback**: Configurable `--poll-interval` (default 500ms), runs in background thread
- **Implementation**: `compiler/watch.py` — ~370 LOC; `CompilationSession` extended with 6 incremental methods

### Test Results

- **251 total tests** (220 existing + 31 new), all passing
- DX-015 (ail rename): 19 tests — scan, change computation, apply, rollback, dry-run, diff, string scanning, import scanning, verification
- DX-016 (ail watch): 12 tests — file hash, cache, incremental compiler initial build, incremental recompile after change, cache update
- Zero regressions: all existing CLI, session, lexer, parser, AST, IR, semantic, runtime, type-checker tests pass

## 0.8.0

### DX-006 — AILang Dependency Ordering Assistant (`ail order`)

- **Tool implementation**: `tools/ail_order/` — analyzes .ail files for dependency ordering issues
- **Function discovery**: `discovery.py` extracts function names, calls, and line numbers from source files
- **Graph analysis**: `graph.py` computes topological levels and detects forward references/cycles
- **Automatic fix mode**: `fixer.py` reorders functions while preserving comments and formatting
- **Report generation**: `reporter.py` produces Markdown and JSON reports for CI/LSP integration
- **CLI integration**: `ail order` command added to compiler CLI with `--json`, `--fix`, `--quiet`, `--stdout` flags
- **Detection capabilities**: 
  - Forward reference violations (function called before definition)
  - Circular function dependencies
  - Unreachable functions (not reachable from main)
  - Duplicate function declarations
- **Project analysis**: Full directory analysis with cross-file insights and report generation
- **12 acceptance tests**, 8 regression tests, 8 AI validation tests — all passing

## 0.4.0

### DX-007 — AILang Language Server

- **Architecture document**: `docs/architecture/LSP_ARCHITECTURE.md` — JSON-RPC, workspace model, document lifecycle, diagnostics pipeline, feature modules, performance goals, testing strategy
- **Shared AST utilities**: New `compiler/lsp/utils.py` consolidating 5× duplicated helpers (`walk_ast`, `find_node_at_offset`, `position_to_offset`, `node_range`, `find_references`, `find_enclosing_call`, `callee_name`, `member_access_name`, `find_definition_target`) into a single source of truth
- **Code duplication eliminated**: `definition.py`, `hover.py`, `references.py`, `rename.py`, `signature_help.py` all refactored to import from `utils.py` — 300+ lines of duplicated code removed
- **Workspace Symbol Search**: `workspace/symbol` implemented — cross-file symbol search with case-insensitive query matching across functions, variables, and imports
- **Code Actions foundation**: `textDocument/codeAction` — quick fix scaffolding for import errors, undefined stdlib references, and unused variable warnings
- **Server capabilities extended**: `workspaceSymbolProvider: true` and `codeActionProvider: true` added to initialize response
- **103 tests**, all passing (up from 99) — 4 new tests for workspace symbols and code actions

## 0.5.0

### DX-008 — AILang Formatter

- **Architecture document**: `docs/architecture/FORMATTER_ARCHITECTURE.md` — canonical style, CLI flags, token-based formatting, comment handling, idempotency requirement, acceptance criteria
- **`ail fmt` CLI**: `--diff` (show changes), `--quiet` (errors only), directory-wide formatting, single-file formatting, stdin mode
- **Token-based formatting**: All 17 token types handled with canonical style rules (4-space indent, space around operators/`:`, newline after `{`, same-line `} else {`)
- **String-aware comment handling**: Inline comments inside string literals preserved (not misidentified as comments)
- **Lexer compatibility**: Reuses existing lexer with zero modifications
- **Repo-wide idempotency**: `--check` mode verifies formatting on all `.ail` files; verified idempotent across the entire repository
- **82 tests**: 71 formatter tests + 11 CLI tests, all passing
- **Zero semantic changes**: no modifications to compiler, runtime, or language specification

### M19 — Documentation Canonicalization

- **Consolidated PROJECT_VISION.md + PROJECT_PHILOSOPHY.md** into `VISION_AND_DIFFERENTIATION.md`
- **Expanded PROJECT_CONSTITUTION.md** with Documentation Rule (§3) and Canonical First Rule (§4)
- **Created `PRODUCT_ROADMAP.md`** at repository root as the single canonical roadmap
- **Moved benchmark methodology** from whitepaper section into `ENGINEERING_BENCHMARK_PLAN.md`
- **Eliminated 7 obsolete/archive files** — ROADMAP.md, PRODUCT_ROADMAP.md (old), etc.
- **Canonical First Rule** added to AGENTS.md workflow and Constitution
- **Cross-references updated** across all affected documents

### Quality Gates

- **854 tests**, all passing (772 existing + 82 new formatter)
- DX-008 (ail fmt): PASS — 82 tests
- Documentation canonicalization: PASS — no broken links

## 0.7.0

### Engineering Optimization Program (Evidence-Driven Stdlib Evolution)

- **Evidence Analysis**: Reviewed B2–B7 benchmark data. Identified stdlib gaps as #1 friction source (42% of B2 errors).
- **`file.listdir(path)`**: New stdlib API returning sorted directory entries. Python `os.listdir()` backend. Available via `import file; file.listdir(path)`.
- **`list.sum(values)`**: New stdlib API returning sum of numeric list items. 3+ independent app pattern threshold met (STDLIB_GAP_ANALYSIS.md).
- **`list.find_by_key(values, key, value)`**: New stdlib API for finding first map in list with matching property. 3+ app threshold met.
- **`convert.to_number(value)`**: Fixed — was a no-op identity function. Now correctly converts string/int to integer (same semantics as `to_int`).
- **`docs/HYPOTHESIS_STATUS.md`**: Created — tracks all 7 engineering hypotheses with evidence status (3 Supported, 1 Partially Supported, 2 Inconclusive, 1 Not Yet Tested).
- **AGENTS.md updated**: Removed `convert.to_number` no-op pitfall. Updated missing stdlib list to reflect available APIs.
- **STDLIB_REFERENCE.md updated**: Added documentation for all 4 new/changed APIs. Updated "Known Missing Operations" section.

### Measured Improvement

| Metric | Before (v0.6.x) | After (v0.7.0) | Improvement |
|--------|:-:|:-:|:-:|
| B2 L2 (CSV pipeline) | 3 iterations | 1 iteration | **67%** |
| B2 total | 7 iterations | 5 iterations | **29%** |
| B2–B6 total | 18 iterations | 16 iterations | **11%** |
| AILang vs Python ratio | 1.38× | 1.23× | **11% closer** |

### Quality Gates

- All new APIs verified: `file.listdir`, `list.sum`, `list.find_by_key`, `convert.to_number` — build+run confirmed
- Existing test suite: 18 stdlib tests pass, zero regressions
- docs/archive/reports/validation/ENGINEERING_EVIDENCE_REPORT.md: updated with before/after comparison
- HYPOTHESIS_STATUS.md: created with evidence references
- All P0 APIs implemented (no scope changes)

## 0.6.2

### B2–B7 — Engineering Benchmark Execution

- **B2 Feature Implementation**: 3 levels (sum_even, CSV pipeline, file diff) in AILang + Python — AILang 2.3× more iterations, all compile-time errors
- **B3 Bug Fix**: 5 bugs (off-by-one, undefined-id, map guard, comparison, infinite recursion) — AILang 1.2× more iterations, 80% first-fix compile rate
- **B4 Refactoring**: Rename + extract function — parity (1.0×), zero regressions in both languages
- **B5 Upgrade**: Signature change + CLI conversion — parity (1.0×), zero regressions
- **B6 Maintenance**: Multi-step feature addition with edge-case handling — parity (1.0×)
- **B7 AI Context**: Structured guide (AGENTS.md + Playbook) saves 3× iterations (1 vs 3 compile-fix cycles)
- **15 benchmark artifacts** created: 5 bug-fix files, naive-without-guide comparison, 2 task specs, 10 code modifications
- **Key stdlib gaps identified**: no `!=` operator, no `listdir`, `convert.to_number` is no-op
- **Evidence published**: `docs/archive/reports/validation/ENGINEERING_EVIDENCE_REPORT.md` with method, datasets, raw results, summary table, and cost model

### Quality Gates

- **docs/archive/reports/validation/ENGINEERING_EVIDENCE_REPORT.md**: PASS — all 6 benchmarks documented with measurements
- B2–B7 artifacts: PASS — all build+run verified

## 0.6.1

### B1.1 — AI Provider Integration & Calibration

- **Provider abstraction**: `benchmarks/providers/base.py` — `AIProvider` abstract base class with `complete(prompt)`, `count_tokens(text)`, and `ProviderResult` data model capturing all measurements (request, prompt, response, timing, interaction, cost)
- **4 provider implementations**:
  - `OpenAIProvider` — GPT-4o, GPT-4, GPT-3.5 (requires `openai` + `tiktoken`)
  - `AnthropicProvider` — Claude 3, Claude 3.5 (requires `anthropic`)
  - `GoogleProvider` — Gemini 1.5, Gemini 2.0 (requires `google-generativeai`)
  - `LocalProvider` — Ollama, vLLM, llama.cpp via OpenAI-compatible API (requires `openai`)
- **Provider factory**: `create_provider(name, model, ...)` with registry and auto-detection from environment variables
- **Calibration module**: `benchmarks/calibration/` — runs identical prompts (short_response, code_understanding, token_counting) across all configured providers to validate measurement infrastructure. Generates immutable calibration reports.
- **B1 extended**: Three priority modes for token measurement — (1) AIProvider for accurate tokenizer + comprehension prompt, (2) manual `ai_results` dict, (3) approximate 4-char heuristic. B1 version bumped to 0.2.0.
- **CLI**: `python -m benchmarks calibrate` and `python -m benchmarks list-providers`
- **Optional dependencies**: Added `[openai]`, `[anthropic]`, `[google]`, `[local]`, `[all]` extras to pyproject.toml
- **37 new tests**: ProviderResult serialization, interface contract, factory, mocked provider implementations (all 4), token estimation, cost estimation, B1 provider integration, calibration execution, schema stability
- **81 tests total** in benchmarks/tests/ (44 existing + 37 new)

### Quality Gates

- **935 tests**, all passing (898 existing + 37 new provider/calibration)
- Provider interface: PASS — all ABC methods implemented, serialization roundtrip verified
- Calibration: PASS — runs against mock providers, reports errors correctly, serializable output

## 0.6.0

### B1 — Engineering Benchmark Framework

- **Generic measurement framework**: `benchmarks/framework/` — runner, metrics, environ, reporting, dataset modules — reusable by B2-B7
- **3 canonical datasets**: small (compiler only), medium (stdlib + docs), current_repo (full repository)
- **Dataset scanning**: Deterministic metadata generation with SHA-256 content hash and repeatability hash
- **Repository metrics**: Full structural analysis (files, LOC, function count, variable count, import count, dependency depth, symbol density, comment ratio, nesting depth, cyclomatic complexity)
- **AI comprehension metrics**: Token estimate, context window utilization, comprehension accuracy (placeholder for future AI integration)
- **Immutable historical results**: Each run stored in `benchmarks/results/<benchmark>/run_<timestamp>/` with measurements, environment snapshot, and human-readable report
- **Summary aggregation**: `benchmarks/results/summary.json` with all runs across all datasets
- **CLI**: `python -m benchmarks {setup,b1,list,test}`
- **44 tests**: 4 runner, 8 dataset, 13 metrics, 9 reporting, 10 B1 integration — all passing
- **Run IDs**: Timestamp-based, sortable, unique
- **.gitignore**: `benchmarks/results/` excluded (runtime artifacts); datasets remain version-controlled

### Quality Gates

- **898 tests**, all passing (854 existing + 44 new B1 framework)
- B1 smoke test: PASS against small, medium, current_repo datasets
- All 3 datasets scan, validate, and produce metrics

## 0.3.1

### DX-006 — AILang Package Manager

- **Manifest parser**: `ail.toml` parsing via `tomllib` with full validation (package name, semver, dependency format)
- **`ail init`**: Project initialization — creates `ail.toml`, `main.ail` stub, and `ail.lock`
- **Local package support**: `path=` dependencies resolved, copied to `lib/<name>/`, full transitive dependency support
- **Git package support**: `git=` dependencies shallow-cloned, tag/branch/rev checkout, transitive support
- **Dependency resolver**: Recursive resolution with topological sort and circular dependency detection
- **Lock file**: `ail.lock` with TOML format, versioned schema, `input_hash` staleness detection, fast replay
- **Checksum verification**: SHA-256 integrity hashing for all installed packages
- **Installation engine**: Full orchestration with `--no-lock`, `--offline`, `--frozen-lockfile` flags
- **Exit codes**: Per TOOLING_ARCHITECTURE.md conventions (0=success, 1=failure, 3=internal error)
- **Acceptance tests**: 8/8 tests passing covering init, parse, install, and lock file generation
- **Documentation**: PACKAGE_MANAGER_DESIGN.md approved, tool README created

### M16 — Documentation Architecture Cleanup

- **ADR collision resolved**: Separate ADR files renumbered ADR-001/002/003 → ADR-010/011/012
- **Status duplication eliminated**: PROJECT_PHASE.md, ROADMAP.md, CURRENT_MILESTONE.md archived; DEVELOPMENT_STATUS.md now canonical
- **AI guidance consolidated**: MASTER_ENGINEERING_PROMPT.md, FOR_FUTURE_AI.md archived; AGENTS.md canonical
- **v0.1.0 sprint reports archived**: 21 files moved to `docs/archive/v0.1.0/`
- **`generated/` added to `.gitignore`**: 9 tracked generated files removed from git tracking
- **Documentation Ownership Matrix created**: 15 document types with canonical owners
- **Cross-references updated**: RELEASE_PROCESS.md, AI_MODEL_GUIDE.md, PROJECT_MEMORY.md

## 0.1.0

### Standard Library v1.0

- **json** — `parse(text)`, `stringify(value)` using Python `json` backend
- **csv** — `parse(text)`, `parse_header(text)`, `stringify(rows)` using Python `csv` backend
- **time** — `now()`, `timestamp()`, `sleep(ms)`, `format(ts)`
- **environment** — `get(name)`, `cwd()`, `args()`
- **random** — `int(min, max)`, `float()`, `choice(collection)`
- **file** — `exists(path)`, `read(path)`, `write(path, content)`, `append(path, content)`, `remove(path)`
- **path** — `join(a, b)`, `basename(path)`, `dirname(path)`, `extension(path)`, `normalize(path)`
- **collections** — `array`, `list`, `map`, `set` with `new`, `get`, `set`, `add`, `contains`, `remove`, `clear`, `keys`, `len`
- **string** — `concat`, `equals`, `uppercase`, `lowercase`, `length`, `contains`, `starts_with`, `ends_with`, `trim`
- **math** — `add`, `sub`, `mul`, `div`, `abs`, `min`, `max`
- **io** — `write`, `writeln`, `println`
- **convert** — `to_string`, `to_int`, `to_bool`, `to_number`
- **system** — `exit`

### Performance, Memory & AI Validation (Phase 5B)

- **Stress tests**: 5000 LOC, 10000 LOC, 50 modules, 100 modules
- **Compile-time benchmarks**: 100/500/1000/5000 LOC with <60s thresholds
- **Memory benchmarks**: LOC-based with <500MB threshold at 5000 LOC
- **Determinism**: IR SHA-256 hash verification across 3 compiles
- **AI validation**: 23 programs generated from public docs, 100% first-pass success
- **Defect fix**: `convert.to_string` was a no-op; added `__native_to_string` builtin

### Developer Ecosystem Foundation (Phase 6)

- **10 documentation guides** created: Installation, Getting Started, Language Tour, Stdlib Reference, Compiler Architecture, Contributor Guide, Testing Guide, Release Process, Roadmap, Documentation Index
- **README rewritten** with badges, quick start, full stdlib table, project status
- **CURRENT_MILESTONE.md** updated to reflect Phase 6 completion

### Quality Gates

- 360 tests, all passing
- black, ruff, mypy all clean

## 0.1.1

### Documentation Consolidation (Phase 7)

- **Canonical specification**: Created `LANGUAGE_SPEC.md` at repository root — single source of truth (860 lines, 16 sections)
- **Fixed LANGUAGE_TOUR.md**: Corrected `else` keyword documentation, removed false "no reassignment" claim, removed wildcard import docs, removed `import "string"` path syntax, updated grammar section to reference canonical spec
- **Archived specifications**: Moved all 9 obsolete design specification files to `archived/specifications/` with ARCHIVED_README.md
- **Updated cross-references**: INDEX.md, CONTRIBUTING.md, PHASE_5B_REPORT.md, PHASE_6_REPORT.md, MASTER_ENGINEERING_PROMPT.md all now point to canonical spec
- **CLI improvements**: Fixed PHASE_6_REPORT.md to reference `ail` CLI instead of `python -m compiler`
- **All quality gates pass**: 374 tests (up from 360), black/ruff/mypy clean

### Validation & Ecosystem Audit (Phase 8)

- **Documentation validation**: 144 code examples tested across 4 documents; all compile and run correctly
- **Standard Library validation**: All 16 modules tested with edge cases and invalid inputs
- **Application validation**: 5/5 large applications compile and execute (Expense Tracker, Inventory, Contact Manager, Banking Ledger, Student Management)
- **Stress validation**: 28/28 tests pass (large LOC, deep nesting, multi-module, determinism)
- **Benchmark validation**: 25/25 tests pass (determinism, compile time, memory, IR hash)
- **AI validation**: 23/23 AI-generated programs compile on first pass (100%)
- **Defect fixes**: Fixed AssertionError crash in AST builder, CLI crash on malformed input, invalid list literal in STDLIB_REFERENCE.md; corrected false float literal and map literal claims in LANGUAGE_SPEC.md
- **408 tests** (up from 374)

### VS Code Extension (Phase 9)

- **Extension structure**: `extensions/vscode-ailang/` with `package.json`, TextMate grammar, snippets, language configuration
- **Syntax highlighting**: 15+ token categories (keywords, builtins, stdlib modules, strings, numbers, operators, comments, functions)
- **Language configuration**: Bracket matching, auto-closing pairs, auto-indentation, folding markers, comment toggling
- **9 snippets**: `main`, `fn`, `if`, `ifelse`, `import`, `return`, `recur`, `let`, `comment`
- **Validation**: 12 test `.ail` files covering all syntax features

### Official Formatter (Phase 10)

- **`ail fmt` command**: Format files in-place, `--check` for CI, `--stdin` for pipelines
- **Single canonical style**: 4-space indentation, same-line braces, spaces around operators, preserved comments
- **Deterministic and idempotent**: Formatting is stable across multiple runs
- **27 formatter tests** + 7 CLI tests
- **Operator precedence parenthesization**: Automatic for correct precedence rendering

### Dogfooding & Real-World Validation (Phase 11)

- **56 AILang applications**: 27 in `apps/`, 29 in `phase11/` — all compile and run
- **Stdlib addition**: `string.substring(value, start, end)` added
- **`env_args` fix**: Now returns user args only (strips CLI plumbing)
- **23 phase11 apps fixed**: Arg index bugs corrected for new `env_args` contract
- **6 new apps built**: find, payroll, library_mgmt, a_star, expr_eval, markdown_parser
- **Linter de-chaining**: Fixed chained member-access-on-call patterns in linter
- **Language freeze declared**: v0.1.x specification frozen — no new keywords, grammar, or syntax changes

### Governance & Philosophy (Phase 11/12)

- **`GOVERNANCE.md`**: Formal proposal process, evidence bars, review process, versioning, backward compatibility, rejected-forever list, freeze policy
- **`LANGUAGE_EVOLUTION.md`**: Permanent record of all 28 feature requests with dispositions
- **`PROJECT_CONSTITUTION.md`**: Immutable rules for development
- **`VISION_AND_DIFFERENTIATION.md`**: Evidence-driven vision, engineering hypothesis, differentiation strategy

### Public Release Preparation (Phase 12)

- **Repository audit**: Removed 9 obsolete/temporary artifacts
- **GitHub readiness**: LICENSE (MIT), SECURITY.md, CODE_OF_CONDUCT.md, SUPPORT.md, issue templates, PR template
- **`RELEASE_CHECKLIST.md`**: Formal release checklist for v0.1.1
- **Documentation audit**: All docs reviewed for broken links, stale examples, version consistency
- **Example validation**: All examples build, run, and produce documented output
- **Installation validation**: Verified from clean environment on Windows
- **VS Code extension**: Verified installation, highlighting, snippets
- **CI/CD**: All workflows verified

### RC1 Fixes

- **`system.exit()` implemented**: Added `system_exit()` native builtin that calls Python's `sys.exit(code)` to properly terminate the process
- **`string.substring` documented**: Added to STDLIB_REFERENCE.md and stdlib tables in README.md and LANGUAGE_SPEC.md
- **Documentation synchronized**: Updated LANGUAGE_TOUR.md to include string module examples and substring workaround
- **Error code constants**: Centralized PAR001, PAR002, PAR003, LEX001, LEX002, LEX003 constants in diagnostics.py
- **Test count corrected**: Updated README.md to show 507 passing tests

## 0.3.0

### Developer Experience

- **DX-004 — Benchmark Runner** completed and accepted (auto-discovery, suite modes, configurable repetition, baseline save/compare, regression detection, CI-friendly exit codes, fault-tolerant execution)
- **DX-005 — Test Generator** completed and accepted (auto-discovery, coverage analysis, three-stage pipeline, intermediate TestCase model, pure Python generators, `--force`/`--dry-run`/`--app` flags, `tests/generated/` separation, dual MD+JSON reports)
- **tools/common/ — extensions**: Added `hashing.py` (SHA-256 file hashing), `discover_apps()`, `list_py_files()`; `run_ail_build()`/`run_ail_run()` already present

### Quality Gates

- **772 tests**, all passing (up from 658)
- DX-004 (ail benchmark): PASS — 11 acceptance + 4 regression + 4 AI validation
- DX-005 (ail testgen): PASS — 9 acceptance + 4 regression + 4 AI validation

## 0.2.1

### Static Analyzer Performance Optimization

- **Replaced 4-pass scan** with single `scan_lines` pass, eliminating redundant function-end detection
- **Replaced character-by-character** `scan_line_calls_inner` with `collect_calls_inner` using `find_substring` builtin
- **Replaced `count_calls_file`** (character-by-character scan of all lines) with `build_calls_from_cache` (derives call statistics from per-function cache)
- **Result:** 3× speedup on hotel_management (252s → 84s), 3× on self-analysis (71s → 24s); self-analysis and large-file analysis now complete (previously never finished)

### Standard Library Additions (ADR-003)

- **`string.find(value, needle)`** — substring search, returns position index or -1
- **`string.find_from(value, needle, start_pos)`** — substring search with start offset
- **`string.split(value, delim)`** — split string into list by delimiter
- Evidence: 8+ independent reimplementations across the app ecosystem satisfied ADR-008 threshold

### Documentation

- **ADR-003** — Decision record for `string.find`/`string.split` stdlib additions
- **v0.2.1 Release Validation Report** — formal checkpoint with 658 tests, benchmark validation, DX acceptance, before/after performance
- **PROJECT_PHASE.md** — documents Platform & Developer Experience Engineering phase
- **PROJECT_CONTEXT.md** regenerated — reflects new stdlib APIs, updated version and test counts

### Quality Gates

- **658 tests**, all passing (up from 624)
- DX-001 (ail context): PASS — 8 acceptance tests, AI validation
- DX-002 (ail doctor): PASS — 9 acceptance tests
- DX-003 (ail static_analyzer): PASS — 8/8 acceptance tests (directory analysis timeout resolved with configurable `--timeout`)

## 0.2.0

### DX Tool #001 — ail context Developer Experience Tool

- **Standalone tool**: `tools/ail_context/` generates `generated/PROJECT_CONTEXT.md` for AI consumption
- **Single-file context**: All project knowledge consolidated into one LLM-optimized document (~6.5KB)
- **15 sections**: Project overview, philosophy, architecture, constraints, milestone, ADRs, stdlib, benchmarks, testing, frozen components
- **Acceptance tested**: 9 functional tests, 6 performance tests, 6 content validation tests, 3 AI validation tests
- **Zero changes**: No modifications to compiler, runtime, or language specification

### Runtime Optimization #001 — Lexical Variable Lookup Cache

- **`Environment.resolve()`** now caches binding locations per-environment in `_resolve_cache: dict[str, Environment]`, eliminating recursive chain walks on repeated variable lookups
- **~6× speedup** on the static analyzer benchmark (373s → 19.5s, the primary bottleneck workload identified by Python profiling)
- **52–64% cache hit rate** across all 5 benchmark apps (dice_roller, hangman_game, inventory_mgmt, kanban, static_analyzer)
- **Negative caching removed**: initial design cached `NameError` sentinels, but `assign` can create new bindings in ancestor environments, making negative entries stale. Only positive results are cached
- **`get_cache_info()` introspection** added to `Environment` and `Runtime` for testing
- **`_CacheStats` instrumentation** added to `Environment` (hits/misses/negative_hits counters) — no semantic effect, used exclusively for profiling
- **102 regression tests** in `tests/test_scope_cache.py` covering basic resolution, shadowing, recursion, reassignment, modules, edge cases, cache introspection, stress, and correctness invariants
- **624 tests total** (522 existing + 102 new), all passing
- **Memory overhead**: ~11 KB for the static analyzer workload (98 cache entries across 18 environments)
- **No semantic changes** — all existing AILang programs remain fully compatible
- **Runtime frozen** after this release. No further optimizations planned until community feedback identifies new bottlenecks

## 0.1.2

### Compiler QA — Bug Fix Sprint #001

- **BUG-001 fixed**: Empty `return;` no longer crashes with `AssertionError` — produces "Return statement requires an expression" diagnostic instead
- **BUG-002 fixed**: Missing initializer `let x = ;` no longer crashes with `AssertionError` — produces "Variable declaration requires an initializer expression" diagnostic instead
- **BUG-003 fixed**: Module name resolution for bare identifiers (`map.set` as a value, not just in call position)
  - `_resolve_name` now checks `self._modules` for bare module names before falling through to `NameError`
  - Module functions are now registered in module environments at initialization time
- **BUG-004 fixed**: Float literal `3.14` no longer produces cryptic "Identifier node missing token" — emits a clear "Float literals are not supported. Use integer division, e.g. 22 / 7" diagnostic at the lexer level (LEX004)
- **Regression tests added**: `test_ast_rejects_empty_return`, `test_ast_rejects_missing_initializer` in `test_ast_builder.py`; `test_regression_module_function_as_value` in `test_validation.py`; `test_lexer_rejects_float_literal` in `test_lexer.py`
- **BUG-005 fixed**: Block-level variable shadowing now works — `_execute_block` creates a new `StackFrame` for each block scope, so `let x` inside an `if`/`else` block properly scopes to that block instead of leaking to the enclosing function
- **BUG-006 fixed**: Deep recursion `count(1000)` no longer crashes — `Runtime.__init__` raises Python's recursion limit from 1000 to 10000 to accommodate AILang function call overhead

### Quality Gates

- **522 tests**, all passing (up from 521)
