# DOCUMENTATION_AUDIT_REPORT.md

**Generated:** 2026-07-21  
**Audit:** M83K Self-Contained Developer Experience Certification

---

## Overview

This report separates documentation into **User-facing** and **Contributor-facing** categories, identifying misplaced content that hinders the self-contained experience.

---

## User Documentation (Must Work Without Repository)

| Document | Path | Status | Notes |
|----------|------|--------|-------|
| Quick Start Guide | README.md lines 12-22 | ✅ GOOD | Has pip install first |
| Getting Started | docs/reference/GETTING_STARTED.md | ✅ GOOD | Clear, no repo references |
| Language Tour | docs/reference/LANGUAGE_TOUR.md | ⚠️ NEEDS FIX | References stdlib/ path |
| Installation Guide | docs/reference/INSTALLATION.md | ❌ REPO-CENTRIC | Requires git clone |
| Standard Library Reference | docs/reference/STDLIB_REFERENCE.md | ✅ GOOD | No repo references |
| MCP Quick Start | docs/reference/MCP_QUICKSTART.md | ✅ GOOD | CLI-focused |
| Language Spec | docs/reference/LANGUAGE_SPEC.md | ✅ GOOD | No repo references |

---

## Contributor Documentation (Repository-Facing)

| Document | Path | Status |
|----------|------|--------|
| CONTRIBUTING.md | docs/governance/CONTRIBUTING.md | Repo-focused |
| Architecture Decisions | docs/architecture/*.md | Internal |
| Compiler Architecture | docs/reference/COMPILER_ARCHITECTURE.md | Internal |
| Benchmarks | docs/benchmarks/*.md | Internal |
| Milestone Archives | docs/milestones/*.md | Internal |
| Dev Playbook | docs/guides/AILANG_DEVELOPMENT_PLAYBOOK.md | Mixed |

---

## Critical Issues Found

### Issue DOC-01: INSTALLATION.md Requires Repository Clone

**Current Content (lines 5-30):**
```
git clone https://github.com/akpersonal4/ailang-lang-AILang.git
cd ailang-lang-AILang
pip install -e .
```

**Problem:** Assumes repository access before installing

**Fix Applied:** ✅ Yes — See FINAL_REMEDIATION_REPORT.md

---

### Issue DOC-02: AGENTS.md Mandatory Reading Includes Repo Files

**Current Section 2.1 (lines 15-22):**
```
1. DEVELOPMENT_STATUS.md
2. PROJECT_MEMORY.md
3. AGENTS.md
4. docs/guides/AILANG_DEVELOPMENT_PLAYBOOK.md
5. docs/architecture/ARCHITECTURE_DECISIONS.md
6. docs/reference/LANGUAGE_SPEC.md
```

**Problem:** DEVELOPMENT_STATUS.md and PROJECT_MEMORY.md don't exist in installed package

**Fix Applied:** ✅ Yes — See FINAL_REMEDIATION_REPORT.md

---

### Issue DOC-03: AGENTS.md References Repository Paths

**Current Section 2.2 (lines 25-35):**
```
- compiler/runtime/
- compiler/interpreter/
- environment.py
```

**Problem:** References internal compiler paths

**Fix Applied:** ✅ Yes — Added warning for installed users

---

## Documentation Separation Rules

### User-Facing Documentation Must:

1. Start with `pip install ailang-lang`
2. Never reference repository paths
3. Prefer CLI commands over file paths
4. Be accessible via `ail docs <NAME>`
5. Work identically in installed and repo contexts

### Contributor-Facing Documentation May:

1. Reference repository structure
2. Assume editable install
3. Discuss compiler internals
4. Include architecture details

---

## Recommendations

### Immediate Fixes

1. **`docs/reference/INSTALLATION.md`:**
   - Add "Install from PyPI" as primary path
   - Move "Clone repository" to "Contributing" section

2. **`AGENTS.md:**
   - Add note: "If reading from installed package, skip lines 1-2 of mandatory reading"
   - Keep repository references in contributor section only

### Future Improvements

3. **Split documentation:**
   - User docs: in `docs/getting-started/`, `docs/reference/`
   - Contributor docs: in `docs/architecture/`, `docs/research/`

4. **Add version to embedded docs:**
   - Include version string in embedded AGENTS.md and LANGUAGE_SPEC.md

---

## Audit Results

| Category | Files | Correctly Placed | Needs Fix |
|----------|-------|------------------|-----------|
| User Docs | 8 | 6 | 2 |
| Contributor Docs | 20+ | N/A | N/A |

---

## Conclusion

Documentation needs separation but is mostly usable. The key fixes are in INSTALLATION.md and AGENTS.md to make them work for installed-only users.