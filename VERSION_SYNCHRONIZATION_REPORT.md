# VERSION_SYNCHRONIZATION_REPORT.md

**Audit:** M91A — Version Synchronization  
**Date:** 2026-07-23  
**Status:** COMPLETE

---

## Canonical Source of Truth

**pyproject.toml** `project.version = "1.1.2"`

All other version references are derived from this source using:
- `scripts/generate_version.py` - syncs to compiler/_version.py
- `scripts/sync_versions.py` - syncs all tool files

---

## Pre-Sync State (v1.1.2 tag - commit ea86dbe)

| File | Version Before |
|------|---------------|
| pyproject.toml | 1.1.1 |
| compiler/_version.py | 1.1.1 |
| tools/ail_context/__main__.py | 1.1.1 |
| tools/ail_mcp/__init__.py | 1.0.5 |
| tools/ail_mcp/server.py | 1.0.8 |
| tools/ail_mcp/context_adapter.py | 1.0.8 |
| README.md badge | 1.1.1 |

---

## Post-Sync State (v1.1.2-rc1 tag - commit cb9451c)

| File | Version After | Source |
|------|--------------|--------|
| pyproject.toml | 1.1.2 | Canonical |
| compiler/_version.py | 1.1.2 | generate_version.py |
| tools/ail_context/__main__.py | 1.1.2 | sync_versions.py |
| tools/ail_mcp/__init__.py | 1.1.2 | sync_versions.py |
| tools/ail_mcp/server.py | 1.1.2 | sync_versions.py |
| tools/ail_mcp/context_adapter.py | 1.1.2 | sync_versions.py |
| README.md badge | 1.1.2 | manual |

---

## Documentation Version References

| File | Updated To | Status |
|------|-----------|--------|
| CHANGELOG.md | v1.1.2 entry added | UPDATED |
| docs/reference/LANGUAGE_SPEC.md | 1.1.2 | UPDATED |
| docs/getting-started/QUICK_START.md | v1.1.2 | UPDATED |
| docs/getting-started/ONBOARDING_CHECKLIST.md | v1.1.2 | UPDATED |

---

## Verification

```
$ python scripts/verify_version.py
All version sources consistent: 1.1.2

$ git diff --stat
 13 files changed, 477 insertions(+), 10 deletions(-)
```

All version references now show **1.1.2**.