# VERSION_DRIFT_ROOT_CAUSE.md

**Audit:** M90.5F — Root Cause Analysis  
**Date:** 2026-07-23  
**Status:** COMPLETE

---

## 1. M90 Observation Summary

M90 Independent Validation reported:
- **repository:** 1.1.0
- **context:** 1.1.1
- **CLI:** 1.1.2

This is a 3-way version mismatch across different components.

---

## 2. Version Component Mapping

| Component | Likely Source | Version Observed | Evidence |
|-----------|--------------|------------------|----------|
| repository | `pyproject.toml` in tested commit | 1.1.0 | Tag v1.1.0 has version = "1.1.0" |
| context | `tools/ail_context/__main__.py` VERSION | 1.1.1 | v1.1.1 tag has VERSION = "1.1.1" |
| CLI | `compiler/_version.py` __version__ | 1.1.2 | Local uncommitted has __version__ = "1.1.2" |

---

## 3. Chain of Events

### Timeline of Version Updates

```
v1.1.0 tag created (commit 590781f9)
├── pyproject.toml: 1.1.0
├── compiler/_version.py: 1.1.0
└── tools/ail_context VERSION: 1.1.0

         ↓ (M83I work: pyproject.toml updated, but generate_version.py NOT run)

v1.1.1 tag created (commit 7a6e663)
├── pyproject.toml: 1.1.1  ← updated
├── compiler/_version.py: 1.1.0  ← NOT updated (generate_version.py not run)
└── tools/ail_context VERSION: 1.1.0  ← NOT updated

         ↓ (M83J work: _version.py manually updated to 1.1.1)

v1.1.2 tag created (commit ea86dbe)
├── pyproject.toml: 1.1.1  ← NOT updated to 1.1.2
├── compiler/_version.py: 1.1.1  ← manually updated (not via generate_version.py)
└── tools/ail_context VERSION: 1.1.1  ← NOT updated

         ↓ (M89 work: local modifications to version files)

Local uncommitted changes
├── pyproject.toml: 1.1.2  ← updated locally
├── compiler/_version.py: 1.1.2  ← updated locally
└── tools/ail_context VERSION: 1.2.0  ← updated locally (beyond 1.1.2)
```

---

## 4. Root Cause Chain

### Primary Cause: Manual Version Management Without Automation

1. **generate_version.py exists but is never run**
   - Script `scripts/generate_version.py` was created in M79.3
   - It was designed to sync `pyproject.toml` version → `compiler/_version.py`
   - **It was never integrated into the release process**

2. **pyproject.toml and _version.py updated independently**
   - v1.1.1: pyproject.toml updated, _version.py not
   - v1.1.2: _version.py manually updated, pyproject.toml not

3. **Tool-specific VERSION constants are independent**
   - `tools/ail_context/__main__.py` has its own VERSION = "1.1.1"
   - Not synchronized with compiler/_version.py

4. **Tags created at wrong times**
   - v1.1.1 tag created before _version.py was corrected
   - v1.1.2 tag created before pyproject.toml was corrected

---

## 5. Evidence

```
# v1.1.1 tag - pyproject.toml says 1.1.1 but _version.py says 1.1.0
$ git show v1.1.1:pyproject.toml | grep "^version"
version = "1.1.1"
$ git show v1.1.1:compiler/_version.py
__version__ = "1.1.0"

# v1.1.2 tag - neither file says 1.1.2
$ git show v1.1.2:pyproject.toml | grep "^version"
version = "1.1.1"
$ git show v1.1.2:compiler/_version.py
__version__ = "1.1.1"
```

---

## 6. Why M90 Saw 1.1.0, 1.1.1, 1.1.2

The most likely explanation:

| M90 Check | Source | Version | Why |
|-----------|--------|---------|-----|
| repository | v1.1.0 tag pyproject.toml | 1.1.0 | Testing v1.1.0 tagged commit |
| context | v1.1.1 tag ail_context | 1.1.1 | Testing v1.1.1 tagged commit |
| CLI | Local wheel (dist/) | 1.1.2 | Testing locally-built wheel |

**M90 tested artifacts from different sources**, not a consistent release.

---

## 7. Conclusion

**Root Cause:** The release process is entirely manual with no automation to keep version files synchronized. The `generate_version.py` script exists but is not run during releases.

**Contributing Factors:**
1. No CI validation on tag pushes
2. No pre-release checklist
3. Tool VERSION constants are independently managed
4. Tags created before version files are updated

**Result:** Version drift across all components, making it impossible to determine what "version 1.1.2" actually means.