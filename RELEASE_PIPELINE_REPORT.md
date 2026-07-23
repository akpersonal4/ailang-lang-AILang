# RELEASE_PIPELINE_REPORT.md

**Audit:** M91C — Release Pipeline  
**Date:** 2026-07-23  
**Status:** COMPLETE

---

## Existing Automation

| Component | Status | Details |
|-----------|--------|---------|
| generate_version.py | EXISTING | Generates _version.py from pyproject.toml |
| verify_version.py | EXISTING | Verifies pyproject.toml matches compiler.__version__ |
| CI version check | EXISTING | In .github/workflows/ci.yml lines 23-37 |

---

## New Automation Added

### 1. scripts/sync_versions.py

Comprehensive version synchronization that updates:
- compiler/_version.py (via generate_version.py logic)
- All tool VERSION/__version__ constants
- README.md badge
- CHANGELOG.md (optional)

**Usage:** `python scripts/sync_versions.py [--dry-run]`

### 2. scripts/release.py

Automated release verification script that performs:
1. Git status check (clean working tree required)
2. Version consistency verification (all files match pyproject.toml)
3. Tag verification (v{version} tag exists)
4. Build step (optional via --skip-build)
5. Artifact verification (wheel metadata and contents)

**Usage:** `python scripts/release.py [--dry-run] [--skip-build]`

---

## Release Workflow

### Recommended Release Process

```bash
# 1. Sync versions from pyproject.toml
python scripts/sync_versions.py

# 2. Verify all versions match
python scripts/verify_version.py

# 3. Commit changes
git add -A && git commit -m "Release v1.1.2 prep"

# 4. Tag the release
git tag -a v1.1.2 -m "Release v1.1.2"

# 5. Build wheel
python -m build

# 6. Verify release artifacts
python scripts/release.py

# 7. Push tag (triggers CI/CD if configured)
git push origin v1.1.2

# 8. Create GitHub Release with wheel/sdist attachments

# 9. Publish to PyPI
twine upload dist/*
```

---

## CI Integration

The existing CI workflow (.github/workflows/ci.yml) already includes:
- Version consistency check (lines 23-37)
- pytest execution
- Format/lint/type checks
- App compilation and execution tests

**Note:** CI does NOT currently run on tag pushes. This should be added for full automation.

---

## Failure Modes

If version mismatches are detected:

```
$ python scripts/release.py
ERROR: Version verification failed!
  compiler/_version.py has 1.1.1, expected 1.1.2
  tools/ail_context/__main__.py has 1.1.1, expected 1.1.2
Exit code: 1
```

The release will **fail** if versions don't match, preventing broken releases.

---

## Recommendations for Future Enhancement

1. **Add tag push trigger to CI** - Run verification on tag push
2. **Add pre-commit hook** - Auto-run sync_versions.py before commit
3. **Add GitHub Actions release workflow** - Automate wheel build and PyPI upload
4. **Add release-please** - Automated changelog and release note generation