# v1.0.0-RC2 — Release Notes

**Release Date:** 2026-07-10
**Version:** 1.0.0-RC2
**Status:** Release Candidate — production-hardened inventory system with authentication, backup/restore, integrity checking, and CSV import

---

## Overview

AILang v1.0.0-RC1 declares the language, compiler, runtime, standard library, and developer tooling **feature-complete and stable** for v1.x. This release marks the transition from pre-1.0 development to public community validation.

**Target use case:** CRUD applications, data processing, and file manipulation (≤2,000 LOC per module).

---

## What's New in v1.0.0-RC2 (Since RC1)

### M38 — Production Inventory Modules (Inventory App)

The inventory reference application (8,515 LOC) is now **production-usable** with the following modules:

| Module | LOC | Purpose |
|--------|:---:|---------|
| `login.ail` | 58 | User authentication with session management (plaintext passwords) |
| `backup.ail` | 120 | Combined JSON backup/restore, auto-backup before every write |
| `validation.ail` | 44 | Input validation (required fields, positive numbers, email, uniqueness) |
| `import_csv.ail` | 53 | CSV import for products, customers, vendors, movements |
| `integrity.ail` | 173 | Data integrity checker (JSON parse, FK refs, negative stock) |

**Storage enhancements:**
- `storage.ail`: Auto-backup before every `storage_save`, corrupted JSON auto-recovery from auto-backup, concurrent access lock (`data/.lock`, 30s stale timeout)

**Main application:**
- `main.ail`: Auth guards on all mutating commands; new CLI commands: `login`, `logout`, `backup`, `restore`, `backups`, `import-*`, `check`

**Config:**
- `config/users.json`: Default `admin/admin123` (admin role) and `staff1/staff123` (staff role)

**Tests:**
- 5 new test files (31 test cases) covering login, backup, validation, import, integrity
- Full suite: 43/43 tests passing

| Metric | RC1 | RC2 |
|--------|:---:|:---:|
| Tests passing | 38/38 | 43/43 |
| Test files | 34 | 39 |
| Production modules | 6 | 11 |
| CLI commands | 16 | 24 |

---

## What's New Since v0.10.0

### DX-015 — Repository Rename Tool (`ail rename`)

- **`ail rename old_name new_name`**: Repository-wide identifier rename with semantic awareness
- **Symbol graph scanning**: Parses all `.ail` files via the compiler pipeline to find function declarations, calls, variable references, parameters, and import segments
- **`--dry-run`**: Preview changes without modifying files
- **`--diff`**: Show unified diff of all changes
- **`--strings`**: Also rename matching string literal values (e.g., map keys)
- **`--no-verify`**: Skip compiler verification after rename
- **Atomic file rewriting** with rollback bundle (`.ail/rename/<timestamp>/`) and automatic restore on failure
- **Implementation**: `compiler/rename.py` — ~260 LOC, no modifications to compiler pipeline

### DX-016 — Watch Mode (`ail watch`)

- **`ail watch [<entry>]`**: Automatic incremental recompilation on file changes
- **Filesystem watcher**: Uses `watchdog` library — cross-platform (Windows `ReadDirectoryChangesW`, macOS `FSEvents`, Linux `inotify`)
- **`--poll`**: Polling-mode fallback for network filesystems, Docker, WSL
- **`--json`**: Machine-readable JSON output for AI tooling integration
- **Incremental compilation**: Only changed module + transitive dependents are re-parsed, re-analyzed, recompiled
- **SHA-256 change detection**: Filters editor atomic-save artifacts
- **Debounce (200ms)**: Prevents redundant compiles during AI burst edits
- **Implementation**: `compiler/watch.py` — ~370 LOC

### Engineering Olympics Gaps Closed

| Gap | Issue | Fix |
|-----|-------|-----|
| **P0 — Arity Validation** | Missing compile-time argument count check | `_check_call_arity` in semantic analyzer; range-based checks for default parameters |
| **P1 — Float Literals** | Lexer rejected `.digits` as `LEX004` | Lexer now consumes `.digits` as part of `NUMBER` token; grammar updated |
| **P2 — Default Parameters** | `fn func(a, b = 10)` not supported | `ParameterNode.default_value` parsed; runtime evaluates defaults fresh per call |
| **P3 — MOD004 Build Fix** | `ail build` failed with MOD004 on all modules | `_compile()` sets `session._root = source_path.parent.resolve()` instead of stdlib dir |

### Stdlib Additions (v0.9.x)

| API | Description |
|-----|-------------|
| `list.sort(values)` | Sort list in-place (ascending) |
| `string.join(values, delimiter)` | Join list of strings with delimiter |
| `list.copy(values)` | Deep copy a list |
| `map.get_or_default(map, key, default)` | Get with fallback default |
| `list.find_by_key(values, key, value)` | Find first map in list matching property |

---

## Version History

| Version | Tag | Key Changes |
|:--------|:---:|-------------|
| v0.1.1 | ✅ | Documentation consolidation, validation audit |
| v0.1.2 | ✅ | Bug fix sprint (6 bugs), `system.exit()` |
| v0.2.0 | ✅ | Runtime Optimization #001 — Variable Lookup Cache (~6× speedup) |
| v0.3.0 | ✅ | DX-004 Benchmark Runner, DX-005 Test Generator |
| v0.4.0 | — | DX-007 Language Server (103 tests) |
| v0.5.0 | ✅ | DX-008 AILang Formatter (82 tests, repo-wide idempotency) |
| v0.6.0 | — | B1 Engineering Benchmark Framework |
| v0.6.1 | — | B1.1 AI Provider Integration (4 providers) |
| v0.6.2 | — | B2–B7 Benchmark Execution (18 iterations total) |
| v0.7.0 | — | Engineering Optimization — `file.listdir`, `list.sum`, `list.find_by_key` |
| v0.8.0 | ✅ | DX-009 Compiler Diagnostics Improvement (`file:line:col`, SEM002 suggestions) |
| v0.9.0 | ✅ | DX-010 Stdlib Expansion — `sort`, `join`, `copy`, `get_or_default`, `filter_by_key` |
| v0.9.1 | ✅ | DX-011 — Inventory 8,515 LOC Reference Application |
| v0.9.2 | ✅ | DX-012 — Python 3.12 Mirror of Inventory System |
| v0.9.3 | ✅ | DX-013 — Engineering Benchmark Infrastructure & AI Harness |
| **v1.0.0-RC2** | **NEW** | M38 — Production inventory modules (login, backup, validation, import, integrity), storage auto-recovery, file locking, test suite 38→43 |
| **v1.0.0-RC1** | **NEW** | DX-014/015/016 — Rename tool, Watch mode, Engineering Olympics closure |

---

## Supported Features

### Language

- Functions with parameters and return values
- Default parameter values (`fn add(a, b = 10)`)
- `let` bindings (block-scoped, lexical, requires initializer)
- `if` / `else` conditionals (no `else if` keyword — use nested `if` in `else`)
- Recursion-only iteration (no `while`/`for` in stable language)
- `return` with required value
- `&&` / `||` logical operators (eager evaluation — both operands always execute)
- Arithmetic: `+` `-` `*` `/` `%`
- Comparison: `==` `!=` `<` `<=` `>` `>=`
- Float literals (`3.14`, `0.5`)
- Integer literals, string literals (`"double quotes"`)
- Member access: `module.func()`, `value.method()`
- Module system: `import path.to.module`, qualified names
- Comments: `//` line comments

### Standard Library (16 modules, 87+ functions)

| Module | Functions |
|--------|-----------|
| `string` | concat, equals, uppercase, lowercase, length, contains, starts_with, ends_with, trim, substring, find, find_from, split, join |
| `math` | add, sub, mul, div, abs, min, max |
| `list` | new, append, len, get, contains, remove, clear, sum, find_by_key, sort, copy |
| `map` | new, set, get, has, delete, keys, clear, get_or_default |
| `array` | new, push, len, get, contains, remove, clear |
| `set` | new, add, contains, len, remove, clear |
| `file` | exists, read, write, append, remove, listdir |
| `path` | join, basename, dirname, extension, normalize |
| `json` | parse, stringify |
| `csv` | parse, parse_header, stringify |
| `time` | now, timestamp, sleep, format |
| `random` | int, float, choice |
| `environment` | get, cwd, args |
| `convert` | to_string, to_int, to_bool, to_number |
| `io` | write, writeln, println |
| `system` | exit |

### Compiler & Tooling

| Tool | Feature | Status |
|------|---------|:------:|
| `ail build` | Compile `.ail` to executable | ✅ |
| `ail run` | Compile and run in one step | ✅ |
| `ail fmt` | Formatter with `--check`, `--diff`, `--quiet`, directory-wide | ✅ |
| `ail lsp` | Language Server (completion, hover, definition, references, rename, signature help, symbols, code actions) | ✅ |
| `ail pkg` | Package Manager (`init`, `install`, lock file, Git dependencies) | ✅ |
| `ail rename` | AST-aware identifier rename with rollback | ✅ |
| `ail watch` | Incremental recompilation on file changes | ✅ |
| `ail order` | Dependency ordering analysis and fix | ✅ |
| `ail testgen` | Test coverage analysis and generation | ✅ |
| `ail benchmark` | Benchmark runner with baseline comparison | ✅ |
| `ail context` | AI onboarding context generation | ✅ |
| `ail doctor` | Repository health check | ✅ |
| `ail static_analyzer` | Code analysis with pattern detection | ✅ |

### Diagnostics

- Error codes: `PAR`, `SEM`, `TYP`, `MOD`, `LEX` with unique numeric codes
- Source locations: `file:line:col`
- Spell-check suggestions for undefined identifiers (SEM002)
- Multi-error collection (all errors in one pass)
- JSON error output (`--json` flag)

---

## Experimental Features

### `for`-in Loops (`--experimental-loops`)

- `for item in collection { body }` syntax, lowered to recursive `__for_fn_N`
- Free variable capture via parameter threading + return-value capture
- Single accumulator support only (multiple writes rejected with clear error)
- **NOT stable for v1.0** — may change in future versions

---

## Benchmark Summary

### Engineering Olympics (AILang vs Python)

| Test | Winner | Result |
|:-----|:------:|:-------|
| P3 — Feature Addition | Python | Python easier (float literals, defaults, loops) |
| P4 — Bug Fix | **AILang** | 5/5 detected vs Python 0/5 |
| P5 — Repository Rename | **AILang** | AST-aware, safer |
| P6 — API Upgrade | Python | mypy detected 4/4 at type-check; AILang runtime only |
| P7 — Maintenance Sprint | Tie | Depends on task type |
| P8 — Security | **AILang** | 5/10 compile-time vs Python 2/10 |

**Overall:** AILang 4/6, Python 2/6

### B2–B7 Engineering Benchmarks

| Benchmark | AILang | Python | Ratio |
|-----------|:------:|:------:|:-----:|
| B2 (Feature Implementation) | 5 iterations | 3 iterations | 1.67× |
| B3 (Bug Fix) | 4 iterations | 3 iterations | 1.33× |
| B4 (Refactoring) | 3 iterations | 3 iterations | 1.0× |
| B5 (Upgrade) | 3 iterations | 3 iterations | 1.0× |
| B6 (Maintenance) | 3 iterations | 4 iterations | **0.75×** |
| **B2–B6 Total** | **18** | **16** | **1.13×** |

### Inventory System (8,515 LOC)

| Metric | AILang | Python | Delta |
|--------|:------:|:------:|:------|
| App LOC | 4,009 | 2,614 | +53% |
| Test LOC | 4,506 | 3,644 | +24% |
| Tests passing | 38/38 | 38/38 | Parity |
| Build/compile time | 0.219s | N/A | — |
| Test run time | 0.173s | 0.194s | **12% faster** |

### Canonical Benchmark Suite

| App | Build (ms) | Run (ms) |
|-----|:----------:|:--------:|
| dice_roller | ~200 | ~220 |
| hangman_game | ~190 | ~260 |
| inventory_mgmt | ~290 | ~340 |
| kanban | ~300 | ~350 |
| static_analyzer | ~290 | ~36,400 |

### Test Suite

- **886+ tests** across compiler, stdlib, CLI, LSP, formatter, DX tools
- **104 test scripts** (59 Python test files + 45 generated)
- **44+ applications** in `apps/` — all build and run
- **66+ total applications** across `apps/`, `ai_benchmarks/`, `examples/patterns/`

---

## Migration Guide

### From v0.x to v1.0.0-RC1

**Breaking changes:** None. The v1.0.0-RC1 release is backward-compatible with all v0.x releases.

**Recommended actions:**

1. **Update import paths** if using the inventory benchmark application — no changes needed for standard API
2. **Rebuild all modules** with `ail build` to pick up new diagnostics (arity validation, float literals)
3. **Review default parameter usage** — now properly supported; remove workarounds
4. **Check for BUG-006 (recursion limit):** Functions deeper than ~500 calls may hit Python's recursion limit. Refactor tail-recursive patterns or decompose into multiple functions.

### If You Used Float Literal Workarounds

Float literals (`3.14`) are now natively supported. Integer-paise arithmetic workarounds can be replaced with decimal literals.

### If You Used Manual Arity Checks

Compile-time arity validation is now active. Remove any runtime argument-counting workarounds.

---

## Support Policy

### v1.x Lifecycle

| Phase | Duration | Scope |
|-------|----------|-------|
| Release Candidate (current) | 4–8 weeks | Community validation, bug reports only |
| v1.0.0 Final | TBD | First stable release |
| v1.x Minor updates | Quarterly | New features, non-breaking enhancements |
| v1.x Patch releases | As needed | Bug fixes, documentation, performance |

### What To Expect

- **Bug reports**: Please file issues at the project repository with minimal reproduction
- **Feature requests**: Accepted but deferred to v1.1+ per the governance policy
- **Backward compatibility**: All v1.0.0-RC1 programs will work unchanged in v1.0.0 final
- **Deprecation**: Any feature removed will have at least one minor release notice

### What RC Means

> v1.0.0-RC1 declares that AILang is feature-complete for its intended use case. The language, compiler, runtime, stdlib, and tooling are stable. All APIs are backward-compatible for the v1.x lifecycle.
>
> This is NOT a declaration that AILang is perfect — it is a declaration that AILang is **finished** in its current form and ready for real-world validation.

---

## Known Bugs

| # | Bug | Severity | Status |
|:-:|-----|:--------:|:------:|
| BUG-006 | Python recursion limit (~500 calls) | Low | Open — documented in spec |
| BUG-007 | Duplicate import silently accepted | Low | Open — scheduled for RC fix |
| BUG-008 | `json.parse` raises `JSONDecodeError` instead of returning `false` on invalid input | Low | Open — runtime builtins need exception wrapping |

See `V1_RC1_KNOWN_LIMITATIONS.md` for full list of limitations and workarounds.

---

## Resources

- **Language spec:** `docs/reference/LANGUAGE_SPEC.md`
- **Stdlib reference:** `docs/reference/STDLIB_REFERENCE.md`
- **Getting started:** `docs/reference/GETTING_STARTED.md`
- **Architecture decisions:** `docs/architecture/ARCHITECTURE_DECISIONS.md`
- **Known limitations:** `docs/releases/V1_RC1_KNOWN_LIMITATIONS.md`
- **Versioning policy:** `docs/releases/V1_VERSIONING_POLICY.md`
- **Changelog:** `CHANGELOG.md`
