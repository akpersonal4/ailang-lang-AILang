# SOURCE_PROVENANCE_REPORT.md

**Audit:** M90.5A — Source Repository Audit  
**Date:** 2026-07-23  
**Status:** COMPLETE

---

## 1. Current Branch State

| Property | Value |
|----------|-------|
| Branch | `main` |
| Upstream | `origin/main` |
| Status | Up to date with origin |
| HEAD | ea86dbea43173e15cce34302b04344e6ab3f99cf |
| HEAD Timestamp | 2026-07-21 15:27:04 -0500 |
| Detached HEAD | No |

---

## 2. Release Tags

| Tag | Type | Target Commit | Annotated Tag Object | Timestamp |
|-----|------|---------------|----------------------|-----------|
| v1.1.0 | annotated | 590781f9ebd77cd10ba747abc7eca0018bbe7b43 | 5640fd74fb8f66811d8af6af244d6404cfe30d4e | 2026-07-20 08:50:36 -0500 |
| v1.1.1 | annotated | 7a6e663de02e3b3f8d045f34f5c898578d507173 | 6dea062e3f9f4faa67d2dbdcbd7dfda2f256469e | 2026-07-21 14:21:16 -0500 |
| v1.1.2 | commit (lightweight) | ea86dbea43173e15cce34302b04344e6ab3f99cf | N/A | 2026-07-21 15:27:04 -0500 |

---

## 3. Tag-to-Version Mapping (Source of Truth Discrepancy)

| Tag | pyproject.toml | compiler/_version.py | tools/ail_context/__main__.py |
|-----|----------------|----------------------|------------------------------|
| v1.1.0 | 1.1.0 | 1.1.0 | 1.1.0 |
| v1.1.1 | 1.1.1 | **1.1.0** (MISMATCH) | 1.1.0 |
| v1.1.2 | **1.1.1** (MISMATCH) | **1.1.1** (MISMATCH) | 1.1.1 |

---

## 4. Uncommitted Changes

**43 files modified, 48 untracked files**

Key modified files with version references:
- `compiler/_version.py` → shows 1.1.2 (local uncommitted change)
- `pyproject.toml` → shows 1.1.2 (local uncommitted change)
- `tools/ail_context/__main__.py` → shows 1.2.0 (local uncommitted change)

---

## 5. GitHub Remote Tags

Remote origin (`origin/main`) contains the same 3 tags (v1.1.0, v1.1.1, v1.1.2) pointing to the same commits.

---

## 6. Evidence

```
$ git describe --tags --abbrev=0
v1.1.2

$ git rev-parse HEAD
ea86dbea43173e15cce34302b04344e6ab3f99cf

$ git rev-parse v1.1.2
ea86dbea43173e15cce34302b04344e6ab3f99cf
```

---

## 7. Summary

1. **HEAD is at commit ea86dbe** which is tagged as v1.1.2
2. **v1.1.2 tag was created on commit ea86dbe** but source files do not reflect version 1.1.2
3. **pyproject.toml in v1.1.2 tag shows 1.1.1**, not 1.1.2
4. **compiler/_version.py in v1.1.2 tag shows 1.1.1**, not 1.1.2
5. **Local uncommitted changes** have updated some files to 1.1.2 and 1.2.0 but not consistently
6. **Working directory is dirty** with 43 modified files

---

## Conclusion

The source repository has version drift between tags and their contained files. The v1.1.2 tag does not contain version 1.1.2 in its version files. This confirms the provenance chain is broken.