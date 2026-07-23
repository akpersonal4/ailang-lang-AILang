# CLI_DISCOVERABILITY_REPORT.md

**Generated:** 2026-07-21  
**Audit:** M83K Self-Contained Developer Experience Certification

---

## Overview

This report verifies that developers can discover everything needed through public CLI commands.

---

## Essential Questions Test

| Question | Answer Method | Status |
|----------|---------------|--------|
| Where is the stdlib? | `ail context --json` shows modules | ✅ WORKS |
| Where are templates? | `ail new <name>` creates them | ✅ WORKS |
| How does module resolution work? | `ail docs LANGUAGE_SPEC` | ✅ WORKS |
| Which modules are built in? | `ail context --json` or `ail docs STDLIB_REFERENCE` | ✅ WORKS |
| Which commands exist? | `ail --help` | ✅ WORKS |
| How do I troubleshoot installation? | `ail doctor` (after fix) | ⚠️ NEEDS FIX |

---

## CLI Commands Audit

### Core Commands (✅ All Working)

| Command | Purpose | Status |
|---------|---------|--------|
| `ail --version` | Version info | ✅ PASS |
| `ail --help` | Help text | ✅ PASS |
| `ail run <file>` | Execute program | ✅ PASS |
| `ail build <file>` | Compile check | ✅ PASS |
| `ail check <file>` | Static validation | ✅ PASS |
| `ail fmt <file>` | Format code | ✅ PASS |
| `ail test` | Run tests | ✅ PASS |
| `ail new <project>` | Create scaffold | ✅ PASS |

### Developer Tools (✅ All Working)

| Command | Purpose | Status |
|---------|---------|--------|
| `ail doctor` | Environment check | ⚠️ PARTIAL (repo assumptions) |
| `ail heal <topic>` | Fix suggestions | ✅ PASS |
| `ail explain <CODE>` | Error explanation | ✅ PASS |
| `ail docs <NAME>` | Documentation | ✅ PASS |
| `ail context --json` | Language context | ✅ PASS |
| `ail mcp` | MCP server | ✅ PASS |

---

## Missing Discoverability

### Issue CLI-01: `ail doctor` Checks Repo Files

After fresh install, running `ail doctor` shows:
- "ailang package: NOT INSTALLED" (wrong module name)
- Missing DEVELOPMENT_STATUS.md (repo-only file)

**Impact:** Confuses new developer about actual installation status

**Fix:** Separate installed-user checks from repository checks

---

### Issue CLI-02: No Direct Stdlib Status Command

Developer question: "Is stdlib loaded correctly?"

Current answer: Run `ail context --json` to infer module list

**Recommendation:** Consider `ail stdlib --status` (optional, not required)

---

## Help Text Quality

### `ail --help` Output

The help text includes:
- Command list with descriptions
- Usage examples
- Recommended workflow

**Finding:** Comprehensive and discoverable

---

## Conclusion

**Status:** ✅ PASS (with one fix needed)

All essential developer questions can be answered through CLI commands. The `ail doctor` tool needs adjustment to serve installed users correctly.