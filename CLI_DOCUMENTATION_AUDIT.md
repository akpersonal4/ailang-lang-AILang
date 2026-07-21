# CLI Documentation Audit

**Date:** 2026-07-21
**Version:** v1.1.1

---

## CLI Commands Verified

| Command | Status | Notes |
|---------|:------:|-------|
| `ail --version` | ✅ | Prints `AILang v1.1.1` |
| `ail --help` | ✅ | Shows all commands, examples correct |
| `ail version` | ✅ | Prints `AILang v1.1.1` |
| `ail new <project>` | ✅ | Creates hello-world template (was inventory) |
| `ail build <file>` | ✅ | Build successful |
| `ail run <file>` | ✅ | Compiles and executes |
| `ail check <file>` | ✅ | Pre-flight validation |
| `ail fmt <file>` | ✅ | Format source |
| `ail test [dir]` | ✅ | Run test files |
| `ail doctor` | ✅ | Environment health check |
| `ail rename` | ✅ | Identifier rename (M83I fix) |

---

## Documentation Cross-Reference

### docs/QUICKSTART.md

| Check | Status |
|-------|--------|
| `ail init` removed | ✅ → `ail new` |
| Expected output matches actual | ✅ |
| Version reference correct | ✅ → v1.1.1 |

### docs/getting-started/QUICK_START.md

| Check | Status |
|-------|--------|
| Version string correct | ✅ → v1.1.1 |
| Workflow steps accurate | ✅ |

### docs/getting-started/ONBOARDING_CHECKLIST.md

| Check | Status |
|-------|--------|
| Version reference correct | ✅ → v1.1.1 |

### README.md (root)

| Check | Status |
|-------|--------|
| Version badge correct | ✅ → v1.1.1 |
| Install instructions correct | ✅ |
| Quick start examples correct | ✅ |

### docs/vscode/INSTALLATION.md

| Check | Status |
|-------|--------|
| VSIX filename correct | ✅ → 1.1.0 (latest available) |
| Install commands correct | ✅ |

---

## Version Consistency (After Fixes)

| File | Version | Status |
|------|---------|--------|
| pyproject.toml | 1.1.1 | ✅ Canonical |
| compiler/_version.py | 1.1.1 | ✅ Fixed |
| compiler/lsp/server.py | 1.1.1 | ✅ Fixed |
| tools/ail_context/__main__.py | 1.1.1 | ✅ Fixed |
| extensions/vscode-ailang/package.json | 1.1.1 | ✅ Fixed |
| extensions/vscode-ailang/package-lock.json | 1.1.1 | ✅ Fixed |
| README.md | 1.1.1 | ✅ |
| docs/QUICKSTART.md | v1.1.1 | ✅ |
| docs/getting-started/QUICK_START.md | v1.1.1 | ✅ |
| docs/getting-started/ONBOARDING_CHECKLIST.md | v1.1.1 | ✅ |
| docs/reference/LANGUAGE_SPEC.md | 1.1.1 | ✅ Fixed |
| docs/architecture/VSCODE_EXTENSION_ARCHITECTURE.md | 1.1.1 | ✅ Fixed |
| DEVELOPMENT_STATUS.md | v1.1.1 | ✅ Fixed |
| PROJECT_MEMORY.md | v1.1.1 | ✅ Fixed |
| CHANGELOG.md | v1.1.1 | ✅ |

---

## Historical Version References (Correct As-Is)

These files contain version references that are historical records and should NOT be updated:

- CHANGELOG.md (lines 19+): v1.1.0, v1.0.x history
- V1.1.0_RELEASE_NOTES.md: Historical release notes
- extensions/vscode-ailang/CHANGELOG.md: Extension history
- docs/benchmarks/*: Historical benchmark results
- docs/governance/LANGUAGE_EVOLUTION.md: Evolution table

---

## Remaining Gaps

| Gap | Severity | Notes |
|-----|----------|-------|
| package-lock.json was at 0.1.1 | Fixed | Now 1.1.1 |
| LANGUAGE_SPEC.md was at 1.0.9 | Fixed | Now 1.1.1 |
| vsix file named 1.1.0 (not 1.1.1) | Low | Rebuild needed for marketplace |
| No `ail --invalid-flag` test coverage | Low | Behavior verified manually |
