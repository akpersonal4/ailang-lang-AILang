# Release Packaging Audit — AILang

**Date:** 2026-07-06
**Auditor:** Independent Release Engineering Lead
**Scope:** Repository packaging for professional open-source distribution

---

## Executive Summary

AILang has the foundations of a professional open-source project (license,
code of conduct, contributing guide, issue/PR templates, CI workflow), but
contains **1 critical, 3 high, and 4 medium** issues that must be addressed
before the repository is ready for public consumption. The single critical
issue — the entire standard library is absent from git — would render every
compilation and benchmark inoperable on a fresh clone.

---

## Critical Issues

### C1. Standard library files not tracked in git

| Property | Value |
|----------|-------|
| **File** | `stdlib/` directory |
| **Evidence** | `git ls-files stdlib/` returns empty. All 16 `.ail` files exist on disk but are absent from the git index. |
| **Impact** | A fresh `git clone` will produce a compiler with no standard library. Every program using `import string`, `import list`, `import json`, etc. (i.e. every benchmark) will fail. The package cannot be distributed. |

### C2. Standard library has no `__init__.py` (compounds C1)

| Property | Value |
|----------|-------|
| **File** | `stdlib/__init__.py` |
| **Evidence** | File does not exist. `pyproject.toml:14-15` declares `packages = ["compiler*", "stdlib*"]`, but setuptools cannot discover `stdlib/` as a package without an `__init__.py`. |
| **Impact** | Even if stdlib files were tracked, they would not be included in `pip install` (non-editable) or any sdist/wheel distribution. |

---

## High Issues

### H1. Missing `py.typed` marker file

| Property | Value |
|----------|-------|
| **File** | `compiler/py.typed` |
| **Evidence** | `pyproject.toml:18` declares `compiler = ["py.typed"]` in package-data. File does not exist on disk. |
| **Impact** | `pip install` will emit a warning/error about missing package data. Downstream tools expecting PEP 561 typed package markers will not detect the compiler as typed. |

### H2. Missing `MANIFEST.in`

| Property | Value |
|----------|-------|
| **File** | `MANIFEST.in` (should exist) |
| **Evidence** | No `MANIFEST.in` present. Without it, source distributions (sdist) produced by `python -m build --sdist` will not include `stdlib/*.ail` or `examples/**/*.ail` files. |
| **Impact** | `pip install ailang` from PyPI (once published) would produce a broken installation with no stdlib. Editable installs (`pip install -e .`) work because they read from the local filesystem. |

### H3. Git tags inconsistent with project version

| Property | Value |
|----------|-------|
| **Evidence** | Three tags exist: `v0.1.1`, `v0.7.0`, `v0.7.0-rc1`. Tag `v0.7.0` is on an older commit than `v0.1.1`. The current `pyproject.toml` declares version `0.1.2`, but no `v0.1.2` tag exists. The version jump from `0.1.x` to `0.7.x` is unexplained and suggests abandoned versioning schemes. |
| **Impact** | Anyone inspecting tags sees a contradictory version history. `git describe` returns `v0.1.1`, not matching `pyproject.toml`'s `0.1.2`. CI or release automation cannot reliably determine the current version from tags. |

---

## Medium Issues

### M1. No runtime dependencies declared

| Property | Value |
|----------|-------|
| **File** | `pyproject.toml` |
| **Evidence** | `[project]` has no `dependencies` key. While the compiler currently uses only Python stdlib, the absence makes the metadata incomplete. |
| **Impact** | Packaging tools may warn. Future addition of a third-party dependency would be invisible to a static audit. |

### M2. No development dependencies section

| Property | Value |
|----------|-------|
| **File** | `pyproject.toml` |
| **Evidence** | No `[project.optional-dependencies]` section exists. The CI workflow and README reference `pytest`, `black`, `ruff`, `mypy` as dev dependencies, but these must be installed manually. |
| **Impact** | Contributors cannot run `pip install -e ".[dev]"`. CI installs dev deps via separate `pip install` commands rather than a canonical extras declaration. |

### M3. Three different version strings in the codebase

| Location | Version |
|----------|---------|
| `pyproject.toml:7` | `0.1.2` |
| `compiler/cli/main.py:25` | `0.1.2` |
| `compiler/lsp/server.py:105` | `0.1.0` |
| `extensions/vscode-ailang/package.json:5` | `0.1.1` |

| Property | Value |
|----------|-------|
| **Evidence** | Four locations, three different version numbers. The LSP server advertises `0.1.0` in its `serverInfo` response. The VS Code extension is at `0.1.1`. The rest is `0.1.2`. No single source of truth for the version string. |
| **Impact** | LSP clients will report the wrong version. The VS Code extension version is out of sync with the compiler it ships with. |

### M4. No authors or maintainers file

| Property | Value |
|----------|-------|
| **Evidence** | No `AUTHORS`, `CONTRIBUTORS`, or `MAINTAINERS.md` file exists. The git log shows a single author. |
| **Impact** | A professional open-source project should document who maintains it, even if currently a single person. |

---

## Low Issues

### L1. No `.gitattributes`

| Property | Value |
|----------|-------|
| **Evidence** | No `.gitattributes` file. Cross-platform contributors may encounter line-ending issues. Common patterns (`*.ail text`, `*.py text diff=python`) are missing. |

### L2. No `.pre-commit-config.yaml`

| Property | Value |
|----------|-------|
| **Evidence** | Pre-commit not configured. CI runs lint/format checks per-push, but there is no local gating before commits. |

### L3. No `.python-version`

| Property | Value |
|----------|-------|
| **Evidence** | Missing. `pyenv`/`asdf` users must manually select Python >=3.11. |

### L4. `.gitignore` missing common patterns

| Property | Value |
|----------|-------|
| **Evidence** | Missing entries for `.coverage`, `htmlcov/`, `.vscode/`, `.idea/`, `.env`, `*.so`, `*.dll`, `*.dylib`. |

### L5. No `FUNDING.yml`

| Property | Value |
|----------|-------|
| **Evidence** | No GitHub Sponsors or funding configuration. Acceptable for early-stage projects but expected for professional ones. |

### L6. `.github/` directory is untracked

| Property | Value |
|----------|-------|
| **Evidence** | CI workflow (`ci.yml`), issue templates, and PR template are all untracked in git. They will not be present on a fresh clone. |

---

## Checklist Summary

| # | Check | Status | Severity |
|:-:|-------|--------|:--------:|
| 1 | Version numbers consistent | **FAIL** — 3 different versions | Medium |
| 2 | Git tags consistent | **FAIL** — v0.7.0 on older commit than v0.1.1 | High |
| 3 | Release notes (CHANGELOG.md) | **PASS** — Comprehensive, covers v0.1.0–v0.1.2 | — |
| 4 | Changelog | **PASS** — Present and detailed | — |
| 5 | Documentation versions consistent | **FAIL** — Multiple stale docs reference v0.1.1 (see previous audit) | Medium |
| 6 | VS Code extension version | **FAIL** — 0.1.1 vs project 0.1.2 | Medium |
| 7 | LICENSE | **PASS** — MIT, present at root and in extension | — |
| 8 | CONTRIBUTING | **PASS** — Comprehensive guide at `docs/CONTRIBUTING.md` | — |
| 9 | SECURITY policy | **PASS** — Present at `SECURITY.md` | — |
| 10 | CODE_OF_CONDUCT | **PASS** — Present at `CODE_OF_CONDUCT.md` | — |
| 11 | GitHub issue templates | **PASS** — Bug report, feature request, config all present | — |
| 12 | Pull request template | **PASS** — Present at `.github/PULL_REQUEST_TEMPLATE.md` | — |
| 13 | Repository badges | **FAIL** — No badges in README.md (no CI status, Python version, license) | Low |
| 14 | Installation instructions | **PASS** — Clear in README.md | — |
| 15 | Build instructions | **PASS** — Documented in README.md and CONTRIBUTING.md | — |
| 16 | CI workflow | **PASS** — Full CI at `.github/workflows/ci.yml` (though untracked) | — |
| 17 | Release workflow | **FAIL** — No release workflow; no automation for PyPI publishing or tag creation | Low |
| 18 | Packaging consistency | **CRITICAL FAIL** — stdlib not tracked, no `__init__.py`, no `MANIFEST.in`, no `py.typed` | Critical |

---

## Priority Remediation Order

| Order | Issue | Severity | Effort | Action |
|:-----:|-------|:--------:|:------:|--------|
| 1 | C1 — stdlib files untracked | Critical | 1 min | `git add stdlib/` and commit |
| 2 | C2 — stdlib missing `__init__.py` | Critical | 1 min | Create empty `stdlib/__init__.py` |
| 3 | H1 — missing `py.typed` | High | 1 min | Create empty `compiler/py.typed` |
| 4 | H2 — missing `MANIFEST.in` | High | 2 min | Create `MANIFEST.in` with stdlib/examples includes |
| 5 | H3 — git tags inconsistent | High | 5 min | Delete tag `v0.7.0` and `v0.7.0-rc1`; add `v0.1.2` at current HEAD |
| 6 | M1 — no `dependencies` declared | Medium | 1 min | Add `dependencies = []` to `pyproject.toml` |
| 7 | M2 — no dev dependencies | Medium | 5 min | Add `[project.optional-dependencies]` with dev extras |
| 8 | M3 — version synchronization | Medium | 2 min | Bump `lsp/server.py` and extension `package.json` to match `0.1.2` |
| 9 | M4 — maintainers file | Medium | 2 min | Create `MAINTAINERS.md` or `AUTHORS.md` |
| 10 | L6 — `.github/` untracked | Low | 1 min | `git add .github/` and commit |
| 11 | L1–L5 — missing config files | Low | 5 min | Create `.gitattributes`, `.pre-commit-config.yaml`, etc. |

---

## Verdict

**The repository is NOT ready for professional open-source distribution as of today.**

The single critical issue (stdlib not tracked in git) makes the project non-functional on a fresh clone — no program using any stdlib module would compile.

However, the remediation is straightforward: approximately 7 files need to be created or added, and git tags need cleanup. Estimated total effort: **20 minutes**. After these fixes, the remaining issues (version string sync, missing config files, untracked CI) are cosmetic or low severity.

The project has strong foundations: comprehensive governance, detailed contributing guide, security policy, code of conduct, issue/PR templates, and a full CI pipeline. The packaging gaps are solvable and likely reflect the project's single-author/pre-release status rather than systemic neglect.
