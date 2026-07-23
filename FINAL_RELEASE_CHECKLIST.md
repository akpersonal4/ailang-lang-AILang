# FINAL_RELEASE_CHECKLIST.md

**Milestone:** M91 — Release Engineering Recovery  
**Date:** 2026-07-23  
**Status:** READY FOR INDEPENDENT VALIDATION

---

## Pre-Release Checklist

### Version Synchronization

- [x] pyproject.toml version = "1.1.2"
- [x] compiler/_version.py synced via generate_version.py
- [x] All tool VERSION constants updated
- [x] README.md badge updated
- [x] CHANGELOG.md entry added
- [x] Documentation version refs updated

### Release Automation

- [x] scripts/sync_versions.py created
- [x] scripts/release.py created
- [x] verify_version.py operational
- [x] CI has version check

### Build & Artifacts

- [x] dist/ailang_lang-1.1.2-py3-none-any.whl built
- [x] dist/ailang_lang-1.1.2.tar.gz built
- [x] Wheel metadata verified (Version: 1.1.2)
- [x] Wheel _version.py verified (__version__ = "1.1.2")

### Release Candidate

- [x] Clean commit created (cb9451c)
- [x] v1.1.2-rc1 tag created
- [x] Tag points to synchronized commit
- [x] Reproducibility verified

---

## Release Candidate Verification (For Independent Validator)

### Required Checks

- [ ] Clone fresh copy of repository
- [ ] Checkout tag v1.1.2-rc1
- [ ] Verify git status is clean (only wheel artifacts in dist/)
- [ ] Run `python scripts/release.py` and verify all checks pass
- [ ] Run `python scripts/verify_version.py` and verify output: "All version sources consistent: 1.1.2"
- [ ] Install wheel: `pip install dist/ailang_lang-1.1.2-py3-none-any.whl`
- [ ] Verify `ail --version` outputs "AILang v1.1.2"
- [ ] Verify `python -c "from compiler import __version__; print(__version__)"` outputs "1.1.2"
- [ ] Verify `pip show ailang-lang | grep Version` outputs "Version: 1.1.2"
- [ ] Run test suite: `pytest tests/ -v --tb=short -x` (expect all pass)
- [ ] Verify documentation references show v1.1.2

---

## Post-Validation Checklist (For Release Publisher)

**ONLY PROCEED AFTER INDEPENDENT VALIDATION PASSES**

### GitHub Release

- [ ] Create GitHub Release from v1.1.2-rc1 tag (rename to v1.1.2 after cleanup)
- [ ] Attach wheel: dist/ailang_lang-1.1.2-py3-none-any.whl
- [ ] Attach source: dist/ailang_lang-1.1.2.tar.gz
- [ ] Copy CHANGELOG.md v1.1.2 entry to release notes

### PyPI Publication

- [ ] Run `twine upload dist/ailang_lang-1.1.2-py3-none-any.whl`
- [ ] Run `twine upload dist/ailang_lang-1.1.2.tar.gz`
- [ ] Verify PyPI page shows version 1.1.2

### Post-Publication Verification

- [ ] pip install ailang-lang==1.1.2
- [ ] Verify `ail --version` shows v1.1.2
- [ ] Confirm PyPI page reflects new version

---

## Version Comparison: Before vs After M91

| Metric | M90.5 State | M91 State |
|--------|-------------|-----------|
| Version files synchronized | NO - tag had 1.1.1 | YES - all 1.1.2 |
| Release automation | NO | YES - sync_versions.py, release.py |
| Clean release candidate | NO - dirty working tree | YES - v1.1.2-rc1 |
| Reproducibility verified | NO | YES |
| Wheel from clean source | NO | YES |
| Documentation consistent | NO - stale refs | YES - all 1.1.2 |

---

## Critical Notes

1. **DO NOT PUBLISH to GitHub or PyPI until independent validation passes**

2. **The original v1.1.2 tag (ea86dbe) is BROKEN** - points to commit with version 1.1.1 files
   - New v1.1.2-rc1 tag (cb9451c) is the correct release candidate

3. **After validation, rename tag:**
   ```bash
   # Delete old broken tag (local only if already pushed)
   git tag -d v1.1.2
   # Rename RC tag to release tag
   git tag -a v1.1.2 -f -m "Release v1.1.2" v1.1.2-rc1
   ```

4. **Push updated tag:**
   ```bash
   git push origin :refs/tags/v1.1.2  # If existed remotely
   git push origin v1.1.2 --force
   ```

---

## Final Status

```
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║         RELEASE CANDIDATE v1.1.2-rc1 IS READY                ║
║                                                               ║
║  Awaiting independent external validation before publication. ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```