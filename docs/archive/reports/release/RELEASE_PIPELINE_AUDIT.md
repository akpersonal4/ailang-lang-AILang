# RELEASE_PIPELINE_AUDIT.md

**Audit:** M90.5E — Release Pipeline Audit  
**Date:** 2026-07-23  
**Status:** COMPLETE - CRITICAL GAPS FOUND

---

## 1. Existing Version Management Tools

| Tool | Location | Purpose |
|------|----------|---------|
| `scripts/generate_version.py` | Root | Reads pyproject.toml version, writes to compiler/_version.py |
| `scripts/verify_version.py` | Root | Verifies all version sources match |
| CI validation step | `.github/workflows/ci.yml:23-37` | Asserts pyproject.toml == compiler.__version__ |

---

## 2. CI/CD Pipeline Analysis

| Trigger | Runs CI? |
|---------|----------|
| push to `develop` | YES |
| pull_request to `develop` or `main` | YES |
| push to `main` | NO |
| tag push | **NO** |

**Critical Gap:** CI does NOT run on tag pushes or main branch commits.

---

## 3. Release Workflow Steps

### What SHOULD Happen (Documented Process)

1. Update version in `pyproject.toml`
2. Run `python scripts/generate_version.py` to sync _version.py
3. Commit changes
4. Create and push tag
5. Build wheel: `python -m build`
6. Publish to PyPI: `twine upload dist/*`
7. Create GitHub Release

### What ACTUALLY Happened

| Step | Status | Evidence |
|------|--------|----------|
| pyproject.toml updated | YES | v1.1.1 and v1.1.2 have different values |
| generate_version.py run | **NO** | _version.py does NOT match pyproject.toml in tags |
| Commit created | YES | Tags exist |
| Tag created | YES | v1.1.0, v1.1.1, v1.1.2 exist |
| Wheel built | YES | dist/ailang_lang-1.1.2-py3-none-any.whl exists |
| PyPI upload | **NO** | HTTP 404 |
| GitHub Release | **NO** | No release objects found |

---

## 4. Version Bump Failures

### v1.1.0 → v1.1.1 Transition

**Tag v1.1.1 created on commit 7a6e663 (Merge branch 'develop')**

| File | After Tag Creation |
|------|-------------------|
| pyproject.toml | 1.1.1 ✓ |
| compiler/_version.py | **1.1.0** ✗ |

**generate_version.py was NOT run.**

### v1.1.1 → v1.1.2 Transition

**Tag v1.1.2 created on commit ea86dbe**

| File | After Tag Creation |
|------|-------------------|
| pyproject.toml | **1.1.1** ✗ (should be 1.1.2) |
| compiler/_version.py | **1.1.1** ✗ (should be 1.1.2) |

**Neither pyproject.toml nor _version.py was updated before tagging.**

---

## 5. GitHub Release Status

```
$ git log --oneline --format="%H %s" --grep="Release" --all
e4e5896 Release Candidate v1.1.0
aa9728d Release v1.1.0 - M77.1 local package manager MVP
5a485ea Release v1.0.11 - M76.3 diagnostics and explain command
f0849b1 Release v1.0.9 - M76.1 arithmetic inference improvements
74333c2 v1.0.1: PyPI publication, documentation closure, M68.6 complete
```

**No GitHub Release objects exist.** Only commit messages mention "Release".

---

## 6. PyPI Publication Status

**No packages have ever been successfully published to PyPI.**

Package name `ailang-lang` was used in pyproject.toml but never uploaded.

---

## 7. Root Cause of Version Drift

The release process has **no automation**:

1. **No pre-release hook** to run `generate_version.py`
2. **No CI on tags** to validate version consistency
3. **No release workflow** to build, package, and publish
4. **Manual process** relying on human memory → errors

---

## 8. Recommendations

1. **Automate version generation** - Add `generate_version.py` to pre-commit hook
2. **Add tag push trigger** to CI for version validation
3. **Create release workflow** using GitHub Actions
4. **Use release-please** or similar for automated changelog and release creation

---

## Conclusion

**The release pipeline is manual and broken.** Version drift occurred because:
1. `generate_version.py` was never run during release
2. Tags were created without updating source files
3. No automation exists to prevent or detect these issues