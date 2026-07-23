# M88_REMEDIATION_MATRIX.md — M89

**Milestone:** M89 — External Validation Remediation  
**Date:** 2026-07-23

---

## Traceability Matrix

| M88 Finding | Severity | Root Cause | Fix | Regression Test | Status |
|-------------|----------|------------|-----|-----------------|--------|
| README version mismatch (1.1.1 vs 1.1.2) | P0 | Badge not updated during release | Updated badge to 1.1.2 | Manual verification of `ail --version` and README | Closed |
| CHANGELOG version mismatch | P0 | No v1.1.2 entry existed | Added v1.1.2 changelog entry | Manual review of CHANGELOG.md | Closed |
| Template missing semicolon | P0 | Template string had `return 0` without `;` | Added semicolon to template | `ail new` → build → verify no fmt needed | Closed |
| Template language version 0.3 | P0 | Hardcoded old version in template | Updated to 1.1.2 | `ail new` → verify ail.toml content | Closed |
| 3 member_access examples fail | P1 | Examples lacked main() and print() | Rewrote examples with main/print | `ail build` + `ail run` on all 3 | Closed |
| recursive_map SEM001 | P1 | Function named `map` collided with stdlib | Renamed to `transform_list` | `ail build examples/patterns/recursive_map.ail` | Closed |
| hotel_management SEM001 | P1 | 3 functions shadowed stdlib builtins | Renamed to hotel_* prefix (26 replacements) | `ail build apps/hotel_management/main.ail` | Closed |
| kanban SEM001 | P1 | `list_copy` shadowed stdlib builtin | Renamed to `kanban_copy_list` | `ail build apps/kanban/main.ail` | Closed |
| inventory_mgmt SEM001 | P1 | `list_copy` shadowed stdlib builtin | Renamed to `inventory_copy_list` | `ail build apps/inventory_mgmt/main.ail` | Closed |
| static_analyzer SEM001 | P1 | `list_copy` shadowed stdlib builtin | Renamed to `analyzer_copy_list` | `ail build apps/static_analyzer/main.ail` | Closed |
| a_star SEM001 | P1 | `list_contains` shadowed stdlib builtin | Renamed to `astar_list_contains` | `ail build phase11/algorithms/a_star.ail` | Closed |
| CLI --help inconsistent | P1 | Core commands lacked --help support | Added --help to 10 commands | `ail <cmd> --help` returns exit 0 | Closed |
| MCP starts server on --help | P1 | No --help check before delegation | Added --help check | `ail mcp --help` shows help, exit 0 | Closed |
| 5 silent examples | P2 | No print() calls | Added print() to all 8 examples | Run each, verify output | Closed |
| Documentation version mismatch | P2 | Hardcoded versions in docs | Updated 5 documentation files | Manual review | Closed |
| Member access syntax docs | P2 | M88 cited `:` syntax; docs use `.` | Verified docs correct, no change needed | Review LANGUAGE_TOUR.md | Closed |

## Summary

| Severity | Found | Fixed | Status |
|----------|:-----:|:-----:|--------|
| P0 | 4 | 4 | All Closed |
| P1 | 7 | 7 | All Closed |
| P2 | 3 | 3 | All Closed |
| **Total** | **14** | **14** | **All Closed** |
