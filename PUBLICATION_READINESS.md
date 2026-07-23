# PUBLICATION_READINESS.md

**Audit:** M90.5G — Publication Readiness  
**Date:** 2026-07-23  
**Status:** NOT READY

---

## 1. Readiness Determination

```
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║                      NOT READY TO PUBLISH                     ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## 2. Critical Blocking Issues

| # | Issue | Severity | Evidence |
|---|-------|----------|----------|
| 1 | **Version files don't match tag** | CRITICAL | v1.1.2 tag has _version.py = 1.1.1, not 1.1.2 |
| 2 | **Build not from clean tag** | CRITICAL | Wheel in dist/ built from uncommitted changes |
| 3 | **Working directory dirty** | CRITICAL | 43 files modified, 48 untracked |
| 4 | **pyproject.toml not updated** | CRITICAL | v1.1.2 tag has pyproject.toml = 1.1.1 |
| 5 | **No GitHub Releases** | HIGH | Tags exist but no release objects |
| 6 | **PyPI never updated** | HIGH | HTTP 404 for ailang-lang |

---

## 3. Pre-conditions for Publication

Before any publication, the following must be true:

| # | Pre-condition | Current Status | Required Action |
|---|---------------|---------------|----------------|
| 1 | All version files synchronized | FAIL | Update pyproject.toml, _version.py, tool VERSIONs to match |
| 2 | Clean commit with synchronized versions | FAIL | Create new commit with consistent versions |
| 3 | Tag points to synchronized commit | FAIL | Create new tag from clean commit |
| 4 | Build from tagged commit | FAIL | Build wheel from new tag |
| 5 | Working directory clean | FAIL | Commit or discard all local changes |
| 6 | GitHub Release created | FAIL | Create release object with artifacts |
| 7 | PyPI upload successful | FAIL | Upload wheel and source dist |

---

## 4. Evidence Summary

```
# Version mismatch in v1.1.2 tag
$ git show v1.1.2:pyproject.toml | grep "^version"
version = "1.1.1"  ← Should be 1.1.2

$ git show v1.1.2:compiler/_version.py
__version__ = "1.1.1"  ← Should be 1.1.2

# Local uncommitted changes not from tag
$ git diff v1.1.2 -- compiler/_version.py
-__version__ = "1.1.1"
+__version__ = "1.1.2"

# Wheel built from wrong source
$ python -c "import zipfile; z=zipfile.ZipFile('dist/ailang_lang-1.1.2-py3-none-any.whl'); print([n for n in z.namelist() if '_version' in n])"
['compiler/_version.py']  # Contains 1.1.2 but tag has 1.1.1
```

---

## 5. Recommended Release Plan

### Phase 1: Clean Up (Before Any Publication)

1. **Synchronize all version files** to a consistent version (e.g., 1.1.2):
   - `pyproject.toml` version
   - `compiler/_version.py` (via `python scripts/generate_version.py`)
   - `tools/ail_context/__main__.py` VERSION
   - `tools/ail_doctor/__main__.py` VERSION
   - `tools/ail_package_manager/__main__.py` VERSION (if exists)
   - `tools/ail_heal/__main__.py` VERSION (if exists)
   - README.md badge
   - CHANGELOG.md (add v1.1.2 entry)

2. **Verify all versions match:**
   ```bash
   python scripts/verify_version.py
   ```

3. **Commit all synchronized changes**

4. **Create clean tag:**
   ```bash
   git tag -a v1.1.2 -m "Release v1.1.2"
   git push origin v1.1.2
   ```

### Phase 2: Build (From Clean Tag)

5. **Verify clean checkout:**
   ```bash
   git checkout v1.1.2
   ```

6. **Build wheel and source dist:**
   ```bash
   python -m build
   ```

7. **Verify built artifacts:**
   - Check _version.py inside wheel matches tag
   - Check METADATA version matches tag

### Phase 3: Release (Publication)

8. **Create GitHub Release:**
   - Use tag v1.1.2
   - Attach wheel and source dist
   - Copy CHANGELOG entry

9. **Publish to PyPI:**
   ```bash
   twine upload dist/ailang_lang-1.1.2-py3-none-any.whl
   twine upload dist/ailang_lang-1.1.2.tar.gz
   ```

10. **Verify PyPI publication:**
    ```bash
    pip install ailang-lang==1.1.2
    ail --version  # Should show 1.1.2
    ```

---

## 6. Artifact Checklist

For a v1.1.2 release, the following must all show version 1.1.2:

- [ ] `pyproject.toml` version
- [ ] `compiler/_version.py` __version__
- [ ] `tools/ail_context/__main__.py` VERSION
- [ ] `tools/ail_doctor/__main__.py` VERSION (if present)
- [ ] `tools/ail_package_manager/__main__.py` VERSION (if present)
- [ ] `tools/ail_heal/__main__.py` VERSION (if present)
- [ ] `README.md` badge
- [ ] `CHANGELOG.md` entry
- [ ] Wheel METADATA version
- [ ] Wheel filename
- [ ] GitHub Release version

---

## 7. Post-Release Verification

After publication, verify with independent check:

```bash
# Install from PyPI
pip install ailang-lang==1.1.2

# Check all version references
ail --version                    # Should be 1.1.2
python -c "from compiler import __version__; print(__version__)"  # 1.1.2
pip show ailang-lang | grep Version  # 1.1.2
```

---

## 8. Summary

**Publication is NOT ready.** The release process requires:

1. A clean, synchronized commit with all version files matching
2. A tag created from that clean commit
3. A wheel built from the tag (not from uncommitted changes)
4. A GitHub Release with attached artifacts
5. Successful upload to PyPI

Currently, none of these conditions are met.

---

## 9. Blocking Issues for M90 Independent Validation

The M90 validator tested artifacts that were:
- **Not from a consistent source** (mixed v1.1.0, v1.1.1, v1.1.2 sources)
- **Not from a clean release** (working directory dirty)
- **Not published** (PyPI 404)

This explains why M90 observed version inconsistencies - they were testing the wrong artifacts.