# Changelog

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
- **`PROJECT_PHILOSOPHY.md`**: Design manifesto — why AILang exists, core principles, non-goals, long-term vision

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

## 0.2.0

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
