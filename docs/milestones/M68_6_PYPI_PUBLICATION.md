# M68.6 — PyPI Publication

**Date:** 2026-07-14
**Status:** In Progress
**Package Name:** `ailang-lang`

---

## Context

M68.5 confirmed package builds clean. `dist/ailang_lang-1.0.0-py3-none-any.whl` exists and is production-ready.

Without PyPI publication, M69 cannot be honestly executed. External developers must be able to run:

```bash
pip install ailang-lang
```

not:

```bash
pip install .
```

---

## Package Naming

```text
Project Name: AILang
PyPI Package: ailang-lang
Distribution Artifact: ailang_lang-1.0.0
CLI Command: ail
```

---

## Pre-Publication Checklist

| Item | Status |
|------|--------|
| Version synced (pyproject.toml = LANGUAGE_SPEC = README) | ✅ |
| Package builds clean | ✅ |
| Entry point configured (`ail = compiler.cli.main:main`) | ✅ |
| MANIFEST.in includes all necessary files | ✅ |
| README.md serves as PyPI description | ✅ |
| LICENSE included | ✅ |

---

## Publication Steps

### 1. Create Project on PyPI

```bash
# Visit https://pypi.org/manage/project/create/
# Project name: ailang-lang
```

### 2. Generate Project-Scoped Token

```bash
# Visit https://pypi.org/manage/project/ailang-lang/settings/tokens/
# Create token with scope: "Entire account (api:write)"
# Save token securely - it will only be shown once
```

### 3. Store Token Locally (DO NOT SHARE)

```powershell
# Option A: Environment variable
$env:TWINE_USERNAME="__token__"
$env:TWINE_PASSWORD="pypi-NEW_TOKEN_HERE"

# Option B: .pypirc file
# Create %USERPROFILE%\.pypirc with:
# [pypi]
# username = __token__
# password = pypi-NEW_TOKEN_HERE
```

### 4. Upload to PyPI

```bash
twine upload dist/*
```

### 5. Verify

```bash
pip install ailang-lang
ail --version
ail new demo
cd demo
ail run main.ail
```

---

## Post-Publication

Once `pip install ailang-lang` works globally:

1. **Update README.md** — Add pip install instructions
2. **Update QUICKSTART.md** — Simplify to `pip install ailang-lang`
3. **Create GitHub Release** — Tag v1.0.0, attach wheel
4. **Proceed to M69** — External developer validation

---

## CI/CD Setup (Recommended)

For long-term maintenance, set up GitHub Actions:

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI
on:
  release:
    types: [published]
jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install build twine
      - run: python -m build
      - run: twine upload dist/*
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
```

Benefits:
- Reproducible releases
- Auditability
- Reduced credential exposure
- Easier rollback

---

## Security Note

**DO NOT share PyPI tokens in chat or commit to source control.**

Tokens should be stored in:
- Local environment variables
- .pypirc file with restricted permissions
- CI/CD secret storage (GitHub Actions Secrets)

---

## Success Criteria

- [ ] Project `ailang-lang` created on PyPI
- [ ] New project-scoped token generated
- [ ] `pip install ailang-lang` works on clean Python 3.11+ environment
- [ ] `ail --version` prints `1.0.0`
- [ ] `ail new demo && cd demo && ail run main.ail` produces output
- [ ] No maintainer intervention required
