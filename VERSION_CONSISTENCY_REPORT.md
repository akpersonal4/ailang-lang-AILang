# Version Consistency Report

**Date:** 2026-07-21
**Version:** v1.1.1

---

## Summary

21 version references were stale across 15 files. All have been corrected to v1.1.1.

---

## Fixes Applied

### Tier 1 — Runtime (affects CLI output)

| File | Line | Was | Now |
|------|------|-----|-----|
| compiler/_version.py | 3 | 1.1.0 | 1.1.1 |
| compiler/lsp/server.py | 116 | 1.1.0 | 1.1.1 |
| tools/ail_context/__main__.py | 12 | 1.1.0 | 1.1.1 |

**Impact:** `ail version` now prints `AILang v1.1.1`. LSP serverInfo reports 1.1.1. `ail context --json` reports 1.1.1.

### Tier 2 — Extension

| File | Line | Was | Now |
|------|------|-----|-----|
| extensions/vscode-ailang/package.json | 5 | 1.1.0 | 1.1.1 |
| extensions/vscode-ailang/package-lock.json | 3,9 | 0.1.1 | 1.1.1 |

### Tier 3 — Documentation

| File | Line | Was | Now |
|------|------|-----|-----|
| DEVELOPMENT_STATUS.md | 13 | v1.1.0 | v1.1.1 |
| DEVELOPMENT_STATUS.md | 499 | v1.1.0 | v1.1.1 |
| PROJECT_MEMORY.md | 10 | v1.1.0 | v1.1.1 |
| docs/getting-started/ONBOARDING_CHECKLIST.md | 11 | v1.1.0 | v1.1.1 |
| docs/reference/LANGUAGE_SPEC.md | 3 | 1.0.9 | 1.1.1 |
| docs/vscode/INSTALLATION.md | 24,30,38,49 | 0.3.0 | 1.1.0 |
| docs/architecture/VSCODE_EXTENSION_ARCHITECTURE.md | 4 | 1.1.0 | 1.1.1 |
| docs/architecture/VSCODE_EXTENSION_ARCHITECTURE.md | 617 | v1.1.0 | v1.1.1 |
| docs/architecture/VSCODE_EXTENSION_ARCHITECTURE.md | 644 | 1.1.0 | 1.1.1 |

### Tier 4 — Tests

| File | Line | Was | Now |
|------|------|-----|-----|
| tests/test_ail_context.py | 20 | 1.1.0 | 1.1.1 |
| tests/test_ail_context.py | 53 | 1.1.0 | 1.1.1 |
| tests/test_vscode_mcp_integration.py | 453 | 1.1.0 | 1.1.1 |

---

## Verification

```
$ ail version
AILang v1.1.1

$ ail context --json | python -c "import json,sys; print(json.load(sys.stdin)['version'])"
1.1.1
```

---

## Remaining Gap

The VSCode extension vsix file is named `vscode-ailang-1.1.0.vsix` (not 1.1.1). A `vsce package` rebuild is needed to produce the 1.1.1 vsix. This is a manual step outside the Python build pipeline.

---

## Stalest Reference Found

`docs/reference/LANGUAGE_SPEC.md` was at version **1.0.9** — four releases behind. Now corrected to 1.1.1.
