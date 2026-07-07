# Distribution Checklist — AILang

**Purpose:** Repeatable steps for publishing each new AILang release.
**Inspired by:** Python Packaging Authority guides, setuptools best practices.

---

## Pre-Release

- [ ] All tests pass: `pytest tests/ -v --timeout=60`
- [ ] All 42 benchmark apps build and run: `ail build apps/<name>/main.ail`
- [ ] `ail version` outputs the intended version string
- [ ] Version synchronized across all files:
  - `pyproject.toml:version`
  - `compiler/cli/main.py:__version__`
  - `compiler/lsp/server.py:VERSION`
  - `extensions/vscode-ailang/package.json:version`
- [ ] No uncommitted changes: `git status --short`
- [ ] CHANGELOG.md updated with release notes

## Packaging

- [ ] `py.typed` exists at package root (PEP 561)
- [ ] `MANIFEST.in` includes all non-Python assets (stdlib `*.ail`, examples)
- [ ] `pyproject.toml` has correct `dependencies` (or empty list)
- [ ] `pyproject.toml` has correct `optional-dependencies.dev`
- [ ] `pyproject.toml` `include` covers all data files
- [ ] sdist builds: `python -m build --sdist`
- [ ] wheel builds: `python -m build --wheel`
- [ ] sdist size is reasonable (not missing files / not bloated)
- [ ] wheel is tagged `py3-none-any` (pure Python)

## Installation Validation

- [ ] Clean clone + `pip install .` succeeds
- [ ] `ail version` works from clean install
- [ ] `ail build stdlib/string.ail` works from clean install
- [ ] `ail run apps/calculator/main.ail` works from clean install
- [ ] `ail help` displays all commands
- [ ] `pip install ".[dev]"` succeeds
- [ ] `pytest tests/` passes from clean install

## Git

- [ ] Tag created: `git tag -a v<major>.<minor>.<patch> -m "AILang v<version>"`
- [ ] Tag pushed: `git push origin v<major>.<minor>.<patch>`
- [ ] No stale or conflicting tags exist: `git tag -l`
- [ ] Release branch merged if applicable: `git log --oneline origin/main..HEAD`

## Distribution

- [ ] **PyPI**: `twine upload dist/*`
- [ ] **GitHub Release**: Create release from tag with changelog
- [ ] **VS Code Marketplace** (if vscode-ailang/ published):
  - `vsce package`
  - `vsce publish`

## Post-Release

- [ ] Bump version to next dev iteration in:
  - `pyproject.toml`
  - `compiler/cli/main.py`
  - `compiler/lsp/server.py`
  - `extensions/vscode-ailang/package.json`
- [ ] Verify `main` branch is clean
- [ ] Announcement drafted (if applicable)

## Per-Release Metadata

| Field | This Release |
|-------|-------------|
| **Version** | v0.1.2 |
| **Date** | 2026-07-06 |
| **Files changed** | 395 |
| **Tests** | 522/522 passing |
| **Apps** | 42/42 building and running |
