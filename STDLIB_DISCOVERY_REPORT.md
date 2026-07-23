# STDLIB_DISCOVERY_REPORT.md

**Generated:** 2026-07-21  
**Audit:** M83K Self-Contained Developer Experience Certification

---

## Overview

This report audits the standard library discovery mechanisms available to developers who only have the installed package.

---

## Current Discovery Tools

### 1. `ail context --json`

**Status:** ✅ WORKS  
**Purpose:** Machine-readable language context  
**Output:**
- Lists all 16 stdlib modules
- Documents available documentation
- Provides workflow and rules

**Evidence:** Works correctly in fresh project directory.

---

### 2. `ail heal missing_import`

**Status:** ✅ WORKS  
**Purpose:** Suggests fixes for import errors  
**Output:**
- Lists available stdlib modules
- Suggests `ail docs STDLIB_REFERENCE` for full list

**Evidence:** Works correctly for basic recovery.

---

### 3. `ail doctor`

**Status:** ❌ BROKEN FOR INSTALLED USERS  
**Purpose:** Repository health checker  
**Issues:**

| Problem | Severity | Description |
|---------|----------|-------------|
| Wrong module check | Critical | Checks `import ailang` instead of `import compiler` |
| Repo-only files | Critical | Checks for DEVELOPMENT_STATUS.md, PROJECT_MEMORY.md |
| Orphan documents | Medium | Walks entire repo for orphan detection |
| Broken links | Medium | Checks repo-wide for broken links |
| Version mismatch | Low | Checks repo files against pyproject.toml |

---

## Stdlib Resolution in Compiler

### `_find_stdlib()` Implementation

Located in `compiler/cli/main.py` (lines 116-179).

**Discovery Chain:**
1. Next to compiler package (highest priority) ✅
2. Next to compiler package parent (editable installs) ✅
3. Walk up from CWD — ONLY in dev mode ✅
4. Fallback to site-packages ✅
5. Last resort ✅

**Production Mode Behavior:**
- NEVER walks upward in production mode
- Correctly finds bundled stdlib in site-packages

**Verification:** Stdlib imports work correctly in fresh project.

---

## Recommendations

### Short Term

1. **Split `ail doctor` into two modes:**
   - Default: Installed environment validation (what stdlib is available, version check)
   - `--repo`: Repository health checks (for contributors)

2. **Add module list to `ail doctor` output:**
   - Show detected stdlib path
   - List available modules

### Long Term

3. Consider adding `ail stdlib` command (optional):
   - Report bundled stdlib status
   - List available modules
   - Check module availability

---

## Conclusion

Stdlib discovery works for compilation, but `ail doctor` needs refactoring to serve installed users appropriately.