# M84R Changelog

## [1.1.2] - 2026-07-22

### Fixed

#### Critical (P0)

- **Stdlib module resolution (I-1):** The compiler now reliably finds standard library modules when installed via `pip install ailang-lang`. Added fallback paths for:
  - `sys.prefix`-based search (virtual environments, conda)
  - `importlib.metadata` RECORD-based discovery
  - Wrapped `site.getsitepackages()` in try/except for virtualenv compatibility
  - Always attempt package-based fallback even when upward walk succeeds

- **`ail doctor` crashes (I-2):** The doctor tool no longer crashes with Python tracebacks. Changes:
  - Detects whether running in the AILang repository or a user project
  - Shows user-facing diagnostics (Python, CLI, ailang, stdlib, project config) for end users
  - Shows full repository health checks for developers
  - Wraps all operations in try/except with actionable error messages
  - Handles KeyboardInterrupt gracefully

#### High (P1)

- **`convert.to_number` behavior (I-3):** Now correctly handles decimal strings. Added `native_to_float` builtin. `convert.to_number("10.5")` returns `10.5` instead of raising an error. `convert.to_int` behavior is unchanged.

- **`ail install`/`ail add` project detection (I-4):** Package manager commands now correctly find `ail.toml` by receiving the project root via `AIL_PROJECT_ROOT` environment variable from the CLI layer.

- **Module resolution documentation (I-5):** Added comprehensive documentation:
  - Module resolution algorithm in `docs/architecture/MODULE_SYSTEM.md`
  - Project setup guide in `docs/reference/GETTING_STARTED.md`
  - Updated installation guide with pip-first workflow
  - Added troubleshooting entries for common module errors

#### Medium (P2)

- **`time.now()` type inference (I-6):** Already handled by existing CallExpressionNode exemption in the type checker. TYP001 is not raised for `let x = time.now();`.

- **`ail heal` usability (I-7):** Now accepts file paths and auto-detects relevant topics from compiler errors. `ail heal myfile.ail` analyzes the file and shows relevant fix suggestions.

#### Low (P3)

- **Scaffold README (I-8):** The `--full` scaffold README now documents what files are included. The default template has no imports and works immediately after `ail new`.
