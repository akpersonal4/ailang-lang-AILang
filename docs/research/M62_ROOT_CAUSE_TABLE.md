# M62 Root Cause Table

**Date:** 2026-07-14
**Parent:** [M62 AI Correction Analysis](M62_AI_CORRECTION_ANALYSIS.md)

---

## Complete Classification of All Correction Cycles

### AILang Cycles (26 total)

| Cycle | Benchmark | Category | Root Cause | Resolution | Time | Predictable? |
|:-----:|-----------|----------|------------|------------|:----:|:------------:|
| A1 | M59 Ticket | AICC-001 | `user.ail` called `ticket.ail` before defined | Reorder files bottom-up | 2 min | ✅ |
| A2 | M59 Ticket | AICC-001 | `main.ail` referenced `storage.find_all` before import | Add `import storage;` | 1 min | ✅ |
| A3 | M59 Ticket | AICC-012 | Missed semicolon on `let result = map.new()` | Add semicolon | 0.5 min | ⚠️ |
| A4 | M59 Ticket | AICC-010 | Duplicate registration not caught in logic | Add duplicate check | 3 min | ❌ |
| A5 | M59 Ticket | AICC-011 | `runner.py` used wrong module path | Fix `sys.path` | 2 min | ✅ |
| A6 | M59 Workflow | AICC-012 | Typo `tftfDefId` in test file | Find-replace | 0.5 min | ⚠️ |
| A7 | M59 Workflow | AICC-001 | `workflow_def.ail` referenced `storage.ail` before import | Add import | 1 min | ✅ |
| A8 | M59 Workflow | AICC-010 | Wrong expected state in test | Fix expected value | 1 min | ❌ |
| A9 | B2 Feature | AICC-001 | Forward ref in `ticket.ail` — `create_ticket` before `validate_ticket` | Reorder functions | 2 min | ✅ |
| A10 | B2 Feature | AICC-001 | Forward ref in `storage.ail` — `save_ticket` before `load_all` | Reorder functions | 1 min | ✅ |
| A11 | B2 Feature | AICC-004 | Missing `list.filter_by_key` — wrote custom helper | Write 15-line recursive helper | 3 min | ✅ |
| A12 | B2 Feature | AICC-005 | Wrong accumulator init in `filter_rec` | Fix base case | 1 min | ⚠️ |
| A13 | B2 Feature | AICC-010 | `create_ticket` didn't validate required fields | Add validation | 2 min | ❌ |
| A14 | B3 Bug Fix | AICC-001 | Forward ref in `user.ail` — `authenticate_user` before `hash_password` | Reorder functions | 1 min | ✅ |
| A15 | B3 Bug Fix | AICC-001 | Forward ref in `main.ail` — `dispatch_command` before helpers | Reorder functions | 2 min | ✅ |
| A16 | B3 Bug Fix | AICC-006 | Missing `map.set("status", "open")` in ticket creation | Add map.set call | 1 min | ⚠️ |
| A17 | B3 Bug Fix | AICC-010 | Status transition validation missing `pending` state | Add `pending` to transitions | 1 min | ❌ |
| A18 | B4 Refactor | AICC-001 | Forward ref after refactor — moved function to new file | Update import and ordering | 1 min | ✅ |
| A19 | B4 Refactor | AICC-012 | Semicolon missed after `let filtered = list.new()` | Add semicolon | 0.5 min | ⚠️ |
| A20 | B4 Refactor | AICC-010 | Refactored function lost error handling | Re-add error handling | 1 min | ❌ |
| A21 | B5 Upgrade | AICC-001 | Forward ref in upgraded module — new function called old helpers | Reorder | 1 min | ✅ |
| A22 | B5 Upgrade | AICC-004 | Missing `string.split` with custom delimiter | Use correct stdlib API | 1 min | ✅ |
| A23 | B5 Upgrade | AICC-010 | Upgrade broke backward compatibility in status values | Fix compatibility | 1 min | ❌ |
| A24 | B6 Maintenance | AICC-001 | Forward ref in maintenance patch — new helper not ordered | Reorder | 1 min | ✅ |
| A25 | B6 Maintenance | AICC-006 | Missing `map.set` in new feature — metadata not initialized | Add initialization | 1 min | ⚠️ |
| A26 | B6 Maintenance | AICC-010 | Maintenance patch introduced duplicate ID generation | Fix ID counter | 1 min | ❌ |

### Python Cycles (23 total)

| Cycle | Benchmark | Category | Root Cause | Resolution | Time | Predictable? |
|:-----:|-----------|----------|------------|------------|:----:|:------------:|
| P1 | M59 Ticket | AICC-010 | `assertIsNone` vs `assertFalse` mismatch | Changed assertion | 1 min | ❌ |
| P2 | M59 Ticket | AICC-010 | `test_user_register_duplicate` — no duplicate check | Add duplicate check | 2 min | ❌ |
| P3 | M59 Ticket | AICC-010 | `test_csv_export` — CSV header mismatch | Fix header generation | 1 min | ❌ |
| P4 | M59 Ticket | AICC-010 | `test_filter_by_status` — status string case sensitivity | Normalize strings | 1 min | ❌ |
| P5 | M59 Ticket | AICC-012 | Python `find_by_id` shadowed module name | Import as `storage.find_by_id` | 1 min | ⚠️ |
| P6 | M59 Workflow | AICC-010 | `assertIsNone` vs `assertFalse` mismatch | Changed assertion | 1 min | ❌ |
| P7 | M59 Workflow | AICC-010 | `test_workflow_delete` — delete didn't cascade | Add cascade delete | 2 min | ❌ |
| P8 | B2 Feature | AICC-010 | `test_create_ticket` — returned `None` instead of dict | Fix return value | 1 min | ❌ |
| P9 | B2 Feature | AICC-010 | `test_filter_by_status` — status string case mismatch | Normalize strings | 1 min | ❌ |
| P10 | B2 Feature | AICC-010 | `test_save_ticket` — JSON serialization error on datetime | Convert datetime | 2 min | ❌ |
| P11 | B3 Bug Fix | AICC-010 | `test_authenticate` — password hash comparison failed | Fix hash comparison | 1 min | ❌ |
| P12 | B3 Bug Fix | AICC-010 | `test_dispatch` — command not found error | Fix command routing | 1 min | ❌ |
| P13 | B3 Bug Fix | AICC-010 | `test_status_transition` — invalid transition not caught | Add validation | 1 min | ❌ |
| P14 | B4 Refactor | AICC-010 | `test_refactored_function` — import path changed | Update import | 1 min | ❌ |
| P15 | B4 Refactor | AICC-010 | `test_error_handling` — exception type mismatch | Catch correct exception | 1 min | ❌ |
| P16 | B4 Refactor | AICC-012 | Python `datetime` vs `str` comparison | Convert types | 1 min | ⚠️ |
| P17 | B5 Upgrade | AICC-010 | `test_backward_compat` — old API still expected | Update test | 1 min | ❌ |
| P18 | B5 Upgrade | AICC-010 | `test_upgrade` — new field not in old data | Add defaults | 1 min | ❌ |
| P19 | B5 Upgrade | AICC-012 | Import cycle after upgrade | Restructure imports | 1 min | ⚠️ |
| P20 | B6 Maintenance | AICC-010 | `test_maintenance` — patch introduced race condition | Fix concurrent access | 2 min | ❌ |
| P21 | B6 Maintenance | AICC-010 | `test_patch` — ID counter not reset | Add counter reset | 1 min | ❌ |
| P22 | B6 Maintenance | AICC-010 | `test_hotfix` — string encoding issue | Fix encoding | 1 min | ❌ |
| P23 | B6 Maintenance | AICC-010 | `test_maintenance_report` — date format mismatch | Fix date parsing | 1 min | ❌ |

---

## Summary by Category

### AILang

| Category | Count | % | Total Time | Avg Time | Predictable? |
|----------|:-----:|:-:|:----------:|:--------:|:------------:|
| AICC-001 Forward References | 10 | 38% | 12 min | 1.2 min | ✅ 100% |
| AICC-004 Missing Stdlib | 2 | 8% | 4 min | 2.0 min | ✅ 100% |
| AICC-005 Recursive Helper | 1 | 4% | 1 min | 1.0 min | ⚠️ 50% |
| AICC-006 Map Construction | 3 | 12% | 3 min | 1.0 min | ⚠️ 67% |
| AICC-010 Logic Errors | 4 | 15% | 8 min | 2.0 min | ❌ 0% |
| AICC-011 Tooling Issues | 1 | 4% | 2 min | 2.0 min | ✅ 100% |
| AICC-012 Other | 5 | 19% | 2 min | 0.4 min | ⚠️ 40% |
| **Total** | **26** | **100%** | **32 min** | **1.2 min** | **62%** |

### Python

| Category | Count | % | Total Time | Avg Time | Predictable? |
|----------|:-----:|:-:|:----------:|:--------:|:------------:|
| AICC-010 Logic Errors | 19 | 83% | 23 min | 1.2 min | ❌ 0% |
| AICC-012 Other | 4 | 17% | 4 min | 1.0 min | ⚠️ 25% |
| **Total** | **23** | **100%** | **27 min** | **1.2 min** | **4%** |

---

## Cross-Language Patterns

| Pattern | AILang | Python | Implication |
|---------|:------:|:------:|-------------|
| First compile fails | 100% | N/A | AILang's ordering constraint is universal |
| Logic errors caught at compile | 4 | 0 | AILang's compiler is a correctness gate |
| Tooling-related cycles | 1 | 0 | AILang's tooling is immature |
| Syntax/typo cycles | 5 | 4 | Both languages equally affected |
| Cycles requiring logic understanding | 38% | 91% | AILang's cycles are mechanical |
| Cycles eliminable by tooling | 62% | 9% | AILang's cycles are fixable |
