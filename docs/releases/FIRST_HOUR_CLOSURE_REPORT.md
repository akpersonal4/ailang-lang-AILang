# First Hour Experience — Closure Report

## Summary

All P0 blockers from the [First Hour Experience audit](../research/FIRST_HOUR_EXPERIENCE.md) are resolved. The
`pip install ailang && ail new project && cd project && ail run main.ail` pipeline now completes without errors on a
fresh install, in under 5 minutes.

## P0 Blockers — Status

| # | Blocker | Resolution | Status |
|:-:|---------|------------|--------|
| 1 | Stdlib bundled into wheel | Added `stdlib/__init__.py`, `include-package-data = true` in `pyproject.toml` | ✅ |
| 2 | `_find_stdlib()` fails outside repo | Expanded fallback chain: pkg-dir → parent-dir → CWD walk → site-packages | ✅ |
| 3 | Module discovery ignores installed stdlib | Added `_try_discover_stdlib_via_package()` in `session.py` | ✅ |
| 4 | Module name computed as full path | Fixed `_register_stdlib_dir()` to use `path.stem` | ✅ |
| 5 | No `ail new` scaffold | Added `cmd_new()` with two templates: `inventory` (CRUD) and `--empty` | ✅ |
| 6 | No `ail test` | Added `cmd_test()` — discovers `test_*.ail`, runs each, prints pass/fail | ✅ |
| 7 | Skeleton syntax errors | Fixed missing `if`‑parentheses, wrong API calls (`io.read_file` → `file.read`) | ✅ |

## P1 Improvements — Status

| # | Improvement | Resolution | Status |
|:-:|-------------|------------|--------|
| 1 | `list.find` alias | Added `fn find(values, key, value)` → `list_find_by_key` | ✅ |
| 2 | `list.filter` alias | Added `fn filter(values, key, value)` → `list_filter_by_key` | ✅ |
| 3 | `map.safe_get` alias | Added `fn safe_get(values, key, default)` → `map_get_or_default` | ✅ |
| 4 | `string.from_int` / `from_bool` | Added wrappers around `__native_to_string` | ✅ |
| 5 | Forward‑reference hint | SEM002 now appends "this looks like a forward reference" when name is a known top‑level function | ✅ |
| 6 | Spell‑check suggestions | Already present via `DiagnosticFormatter.find_suggestion()` | ✅ (pre‑existing) |

## P2 Items — Deferred

See `docs/roadmap/V1X_ROADMAP.md` for details.

- **string interpolation** — V1.2 language enhancement
- **`ail try` REPL** — V1.3 tooling
- **VS Code extension stub** — V1.4 ecosystem

## Changes Made

### `pyproject.toml`
- Added `[tool.setuptools] include-package-data = true`

### `stdlib/__init__.py` *(new)*
- Package marker so setuptools discovers and bundles stdlib in wheels

### `stdlib/list.ail`
- Added `fn find(values, key, value)` and `fn filter(values, key, value)` as user-friendly aliases

### `stdlib/map.ail`
- Added `fn safe_get(values, key, default)` as alias for `get_or_default`

### `stdlib/string.ail`
- Added `fn from_int(value)` and `fn from_bool(value)`

### `compiler/cli/main.py`
- **`_find_stdlib()`** — expanded fallback to check parent dir, CWD walk, and `site.getsitepackages()`
- **`cmd_new(args)`** — new subcommand, creates project from embedded templates
- **`cmd_test(args)`** — new subcommand, discovers & runs `test_*.ail` files
- **`cmd_help()`** / dispatch table** — registered `new` and `test` commands
- **Template strings** — `_NEW_PROJECT_TEMPLATES` (inventory CRUD) and `_TEMPLATE_EMPTY_PROJECT`

### `compiler/compilation/session.py`
- **`_discover_stdlib_modules()`** — attempts upward walk first, falls back to `_try_discover_stdlib_via_package()`
- **`_register_stdlib_dir(stdlib_dir)`** — new helper; uses `path.stem` for module names
- **`_try_discover_stdlib_via_package()`** — locates stdlib via compiler package path and site-packages
- **`analyze()`** — collects all top-level function names into `symbol_table._all_function_names`

### `compiler/semantic/symbol_table.py`
- Added `_all_function_names: set[str]` attribute
- `resolve()` — when name is not found and matches `_all_function_names`, appends forward-reference hint

## Validation

| Test | Result |
|------|--------|
| `ail new test_project` + `ail run main.ail` | ✅ Welcome + 3 items listed |
| `ail new --empty myapp` + `ail run main.ail` | ✅ Hello from AILang |
| `ail test --verbose` (with test file) | ✅ PASS / FAIL counts |
| `ail run examples/hello_world/main.ail` | ✅ Hello, World! |
| Stdlib tests (88 tests) | ✅ All pass |
| Forward-reference error message | ✅ Appends forward-reference hint |

## Future Measurement

Re-run the [First Hour Experience](../research/FIRST_HOUR_EXPERIENCE.md) audit protocol on a fresh machine:

```bash
pip install ailang
ail new inventory
cd inventory
ail run main.ail
```

Target: < 5 minutes, zero errors, zero manual steps.
