# Release Checklist

**Use this checklist for every AILang release.**

---

## v0.1.1

### Pre-Release

- [x] All quality gates pass (pytest, black, ruff, mypy)
- [x] 507 tests passing
- [x] CHANGELOG.md updated with all changes
- [x] Version consistent across `pyproject.toml`, `README.md`, `PROJECT_STATE.json`
- [x] Repository audit complete (no temp files, no stale artifacts)
- [x] GitHub readiness files in place (LICENSE, SECURITY.md, CODE_OF_CONDUCT.md, SUPPORT.md)
- [x] Issue/PR templates in `.github/`
- [x] Documentation audit complete (no broken links, stale examples, incorrect CLI output)
- [x] All examples build and run
- [x] Installation verified from clean environment
- [x] VS Code extension verified (installation, highlighting, snippets)
- [x] Language freeze declared (v0.1.x — no syntax/grammar/semantic changes)
- [x] Governance documents in place (GOVERNANCE.md, LANGUAGE_EVOLUTION.md, PROJECT_PHILOSOPHY.md)
- [x] All 26 applications in apps/ compile successfully
- [x] All 26 applications in apps/ run successfully
- [x] No TODO/FIXME/HACK/XXX comments in codebase
- [x] Public API audit complete (all stdlib functions documented)

### Release Steps

- [ ] Tag the release: `git tag -a v0.1.1 -m "Release v0.1.1"`
- [ ] Push the tag: `git push origin v0.1.1`
- [ ] Create GitHub Release with title `v0.1.1` and CHANGELOG content as description
- [ ] Package VS Code extension for release
- [ ] Update PROJECT_STATE.json with final release data
- [ ] Communicate release to community

### Post-Release

- [ ] Monitor issue tracker for release-related bug reports
- [ ] Set next milestone in roadmap
- [ ] Begin Phase 0.2.0 planning (if applicable)

---

## Release Template

```markdown
# AILang v0.1.1

## Overview

AILang is an AI-first programming language designed to be deterministic,
specification-driven, and easy for both humans and AI systems to reason about.

This is the first public release of AILang.

## What's New Since v0.1.0

- 408 passing tests (up from 360)
- VS Code extension with syntax highlighting and snippets
- Official formatter (`ail fmt`)
- 56 real-world AILang applications
- Complete governance framework
- Language freeze declared for v0.1.x

## Installation

```bash
git clone https://github.com/anomalyco/ailang.git
cd ailang
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/macOS
pip install -e .
pip install pytest black ruff mypy
```

## Documentation

- [Getting Started](docs/GETTING_STARTED.md)
- [Language Tour](docs/LANGUAGE_TOUR.md)
- [Stdlib Reference](docs/STDLIB_REFERENCE.md)
- [Language Specification](LANGUAGE_SPEC.md)
```

---

## Tagging Convention

| Release | Tag | Description |
|---------|-----|-------------|
| v0.1.0 | `v0.1.0` | Initial stdlib release |
| **v0.1.1** | **`v0.1.1`** | **Public release — ecosystem & governance** |
| v0.2.0 | `v0.2.0` | (Future) Evidence-based language improvements |
