# Packaging Report — AILang v0.1.2

**Date:** 2026-07-06
**From:** RELEASE_PACKAGING_AUDIT.md findings

---

## Issues Resolved

| # | Issue | Severity | Action Taken |
|:-:|-------|:--------:|--------------|
| C1 | stdlib/ files not tracked in git | Critical | `git add stdlib/` — all 16 `.ail` files + `__init__.py` now tracked |
| C2 | stdlib/ has no `__init__.py` | Critical | Created `stdlib/__init__.py` (empty) for setuptools discovery |
| H1 | Missing `py.typed` marker | High | Created `compiler/py.typed` (empty) |
| H2 | Missing `MANIFEST.in` | High | Created with `stdlib/*.ail` and `examples/*.ail` recursive includes |
| H3 | Git tags inconsistent | High | Deleted `v0.7.0` and `v0.7.0-rc1`; added `v0.1.2` at HEAD |
| M1 | No `dependencies` declared | Medium | Added `dependencies = []` to `[project]` |
| M2 | No dev dependencies section | Medium | Added `[project.optional-dependencies] dev` with pytest, black, ruff, mypy |
| M3 | Version strings inconsistent | Medium | LSP server: `0.1.0`→`0.1.2`; VS Code extension: `0.1.1`→`0.1.2` |
| M4 | No maintainers file | Medium | Created `AUTHORS.md` |
| L1 | No `.gitattributes` | Low | Created with text/binary detection, LF normalization, Python/AILang patterns |
| L2 | No pre-commit config | Low | Not created (out of scope for this sprint) |
| L3 | No `.python-version` | Low | Not created (not critical for packaging) |
| L4 | `.gitignore` missing patterns | Low | Added coverage, IDE, env, compiled extension patterns |

## Files Created

| File | Purpose |
|------|---------|
| `compiler/py.typed` | PEP 561 typed package marker |
| `stdlib/__init__.py` | Package discovery for setuptools |
| `MANIFEST.in` | sdist inclusion of stdlib and examples |
| `.gitattributes` | Cross-platform line-ending normalization |
| `AUTHORS.md` | Project maintainer documentation |

## Files Modified

| File | Change |
|------|--------|
| `pyproject.toml` | Added `dependencies = []` and `[project.optional-dependencies] dev` |
| `compiler/lsp/server.py` | Version `0.1.0` → `0.1.2` |
| `extensions/vscode-ailang/package.json` | Version `0.1.1` → `0.1.2` |
| `.gitignore` | Added coverage, IDE, env, compiled extension patterns |

## Files Tracked (previously untracked)

| Directory | Contents |
|-----------|----------|
| `stdlib/` | 16 `.ail` modules + `__init__.py` |
| `examples/` | 8 demo `.ail` files + 10 pattern `.ail` files |
| `compiler/lsp/` | LSP server, protocol, 7 feature modules |
| `compiler/formatter.py` | Code formatter |
| `compiler/__main__.py` | `python -m compiler` entry point |
| `tests/` | 16 new test files (formatter, LSP, benchmarks, stdlib, stress) |
| `apps/` | 42 benchmark application directories |
| `.github/` | CI workflow, bug/feature issue templates, PR template |
| `docs/` | Essential documentation (INSTALLATION, LANGUAGE_TOUR, etc.) |

## Git Tags

| Tag | Status | Target |
|-----|--------|--------|
| `v0.1.1` | Preserved | Previous stable release |
| `v0.7.0` | **Deleted** | Conflicting tag on older commit |
| `v0.7.0-rc1` | **Deleted** | Conflicting tag on older commit |
| `v0.1.2` | **Created** | Current HEAD |
