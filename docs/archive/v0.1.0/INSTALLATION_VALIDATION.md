# Installation Validation — AILang v0.1.2

**Date:** 2026-07-06
**Environment:** Windows 11, Python 3.11.15

---

## Method: Clean Clone → pip Install

1. `git clone <repo>` from local path
2. `python -m venv .venv_test`
3. `.venv_test\Scripts\pip install .`

## Results

| Step | Result |
|------|--------|
| Clone | ✓ — Tag `v0.1.2` present |
| Wheel build | ✓ — `ailang-0.1.2-py3-none-any.whl` (74 KB) |
| pip install | ✓ — `Successfully installed ailang-0.1.2` |

## CLI Smoke Tests

| Command | Exit Code | Output |
|---------|:---------:|--------|
| `ail version` | 0 | `AILang v0.1.2` |
| `ail help` | 0 | All 8 commands listed |
| `ail build stdlib/string.ail` | 0 | `Build successful` |
| `ail build apps/calculator/main.ail` | 0 | `Build successful` |
| `ail run apps/calculator/main.ail` | 0 | Calculator output correct |
| `ail run apps/kanban/main.ail` | 0 | Kanban board loads correctly |

## Full Test Suite

```
.package test session — 522 passed in 13.88s
```

| Category | Passed |
|----------|:------:|
| `tests/test_compiler.py` | All passed |
| `tests/test_formatter.py` | All passed |
| `tests/test_lsp.py` | All passed |
| `tests/test_validation_comprehensive.py` | All 294 passed |
| All benchmark `apps/` | 42/42 build and run |

## Dev Extras

`pip install ".[dev]"` installed all dev dependencies (pytest, black, ruff, mypy, click, librt, pytokens, ast-serialize).

## Verdict

**PASS** — Package installs, CLI works, toolchain builds, and all 522 tests pass on a clean clone.
