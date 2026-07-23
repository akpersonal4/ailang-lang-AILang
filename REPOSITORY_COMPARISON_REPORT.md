# REPOSITORY_COMPARISON_REPORT.md

**Audit:** M90.5C — GitHub vs PyPI Comparison  
**Date:** 2026-07-23  
**Status:** COMPLETE

---

## 1. GitHub Repository

| Property | Value |
|----------|-------|
| URL | https://github.com/akpersonal4/ailang-lang-AILang |
| Default Branch | main |
| Remote Tags | v1.1.0, v1.1.1, v1.1.2 |
| GitHub Releases | **NONE** |

---

## 2. PyPI Package

| Property | Value |
|----------|-------|
| `ailang` | HTTP 404 Not Found |
| `ailang-lang` | HTTP 404 Not Found |
| Published Versions | **NONE** |

---

## 3. Version Comparison Table

| Component | GitHub (v1.1.2 tag) | PyPI | Local Wheel |
|-----------|---------------------|------|-------------|
| pyproject.toml version | 1.1.1 | N/A | 1.1.2 |
| _version.py | 1.1.1 | N/A | 1.1.2 |
| Package metadata | N/A | Not published | 1.1.2 |

---

## 4. Artifact Comparison

| Artifact | GitHub | PyPI | Local dist/ |
|----------|--------|------|-------------|
| Wheel file | NO | NO | YES (1.1.2) |
| Source distribution | NO | NO | YES (1.1.2) |
| GitHub Release | NO | N/A | N/A |
| README | YES | NO | YES |
| CHANGELOG | YES | NO | YES |

---

## 5. Key Discrepancies

1. **GitHub has no releases** - Tags exist but no GitHub Release objects
2. **PyPI is empty** - No packages published
3. **Version mismatch in tags** - v1.1.2 tag contains version 1.1.1 files
4. **Local wheel is ahead of tags** - Built from uncommitted changes

---

## 6. Evidence

```
$ curl -s https://pypi.org/pypi/ailang-lang/json
HTTP 404 Not Found

$ git ls-remote --tags origin
590781f9ebd77cd10ba747abc7eca0018bbe7b43	refs/tags/v1.1.0
...
ea86dbea43173e15cce34302b04344e6ab3f99cf	refs/tags/v1.1.2

$ git log --oneline --format="%H %s" --grep="Release" --all | head -10
(no GitHub releases found)
```

---

## Conclusion

**GitHub and PyPI relationship is not established.** Tags exist on GitHub but no releases were created. PyPI has never received any packages. The local `dist/` wheel was built but never published.