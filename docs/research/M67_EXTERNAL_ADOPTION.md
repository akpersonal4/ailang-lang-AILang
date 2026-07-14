# M67 — External Developer Adoption Validation

**Date:** 2026-07-14
**Status:** PROTOCOL COMPLETE — REQUIRES EXTERNAL DEVELOPER
**Author:** big-pickle (maintainer, not test subject)

---

## 1. Critical Finding

**This milestone cannot be executed by the maintainer.**

The entire premise of M67 is to validate whether an **external developer with no prior AILang knowledge** can become productive without maintainer assistance. As the creator of AILang, I have deep knowledge of:

- Compiler internals and expected behavior
- Language design rationale
- Common pitfalls and workarounds
- Documentation gaps (and how to navigate around them)

Any test I run would be **invalid** — I would know what to expect and how to work around issues that would genuinely block an external developer.

**What M67 requires:** A real external developer, recruited from outside the project, who has never seen AILang code before.

---

## 2. Test Protocol

### 2.1 Phase 1 — Fresh Developer Environment

**Setup (maintainer performs before developer arrives):**

```bash
# 1. Clean virtual environment
python -m venv fresh_env
source fresh_env/bin/activate  # or fresh_env\Scripts\activate on Windows

# 2. Install AILang (if published to PyPI)
pip install ailang

# OR install from source (if not on PyPI)
git clone https://github.com/anomalyco/opencode.git ailang_install
cd ailang_install
pip install -e .

# 3. Verify installation
ail version

# 4. Open VS Code with fresh profile (no extensions except AILang)
code --new-window --profile fresh

# 5. Start recording (screen capture + keystroke logging)
```

**Developer receives:**
- Clean machine with Python 3.11+, VS Code, Git
- No prior knowledge of AILang
- No access to maintainer
- No access to source code

**Allowed resources:**
- README.md (and linked documentation)
- examples/ directory
- VS Code extension
- CLI help output (`ail help`)

**Forbidden:**
- Source code reading
- Asking maintainers
- Hidden knowledge

### 2.2 Phase 2 — First Hour Experience

**Tasks (in order):**

| # | Task | Time Limit | Success Criterion |
|:-:|------|:----------:|-------------------|
| 1 | Install AILang | 5 min | `ail version` returns version |
| 2 | Create project | 5 min | `ail new my_first_app` succeeds |
| 3 | Build hello world | 5 min | `ail run main.ail` returns 0 |
| 4 | Add package dependency | 10 min | `ail add some_package` succeeds |
| 5 | Write tests | 10 min | `ail test` passes |
| 6 | Run tests | 5 min | Tests execute and report results |
| 7 | Use for-in loops | 10 min | Loop compiles and runs correctly |
| 8 | Publish package | 10 min | `ail publish` succeeds |
| 9 | Use VS Code extension | 5 min | Syntax highlighting + LSP work |
| 10 | Fix one compiler error | 5 min | Error message leads to fix |

**Measurements:**
- Time spent on each task
- Errors encountered
- Documentation pages visited
- Correction cycles per task
- Cognitive load (self-reported: 1-5 scale)

### 2.3 Phase 3 — 500 LOC Application

**Application:** Mini Task Manager

**Requirements:**
- CRUD operations (create, read, update, delete)
- Search (by title, description)
- Persistence (JSON file)
- Reports (tasks by status, by priority)
- Permissions (admin, user roles)
- Audit log (track changes)

**Target:** 500-700 LOC

**Measurements:**
- First compile success rate
- Total correction cycles
- Final LOC
- Developer confidence score (1-10)

### 2.4 Phase 4 — Python Comparison

**Same developer, same AI, same task.**

**Measurements:**
- Onboarding time (AILang vs Python)
- Documentation usage
- Correction cycles
- Perceived difficulty (1-10)
- Completion rate

---

## 3. Measurement Framework

### 3.1 Metrics Collection

| Metric | Method | Unit |
|--------|--------|------|
| Time per task | Stopwatch | Minutes |
| Errors encountered | Manual count | Count |
| Documentation pages visited | Browser history | Count |
| Correction cycles | Manual count | Count |
| Cognitive load | Self-reported | 1-5 scale |
| First compile success | Binary | Pass/Fail |
| Total LOC | `wc -l` or manual | Lines |
| Developer confidence | Self-reported | 1-10 scale |
| Onboarding time | Stopwatch | Minutes |
| Perceived difficulty | Self-reported | 1-10 scale |

### 3.2 Scoring

| Category | Weight | Scoring |
|----------|:------:|---------|
| Time to complete | 30% | Linear (faster = better) |
| Error count | 25% | Linear (fewer = better) |
| Correction cycles | 25% | Linear (fewer = better) |
| Developer confidence | 20% | Self-reported |

### 3.3 Success Criteria

| Criterion | Threshold | Required? |
|-----------|:---------:|:---------:|
| Installation | < 5 minutes | Yes |
| Hello World | < 5 minutes | Yes |
| First package | < 10 minutes | Yes |
| 500 LOC application | < 4 hours | Yes |
| Correction cycles | <= Python | Yes |
| Maintainer intervention | 0 | Yes |
| Developer confidence | >= 8/10 | Yes |

---

## 4. Documentation Audit Results

### 4.1 Critical Gaps (Blockers)

| # | Gap | Severity | Impact |
|:-:|-----|:--------:|--------|
| 1 | All 8 README doc links are broken | Critical | Developer cannot access any documentation |
| 2 | STDLIB_REFERENCE missing 21+ functions | Critical | AI generates incorrect fallback implementations |
| 3 | Examples have zero documentation | High | Developer cannot learn from examples |
| 4 | QUICKSTART has wrong Python version | High | Developer on 3.9/3.10 hits cryptic errors |
| 5 | No PyPI publication evidence | High | Developer cannot install without cloning |

### 4.2 Moderate Gaps

| # | Gap | Severity | Impact |
|:-:|-----|:--------:|--------|
| 6 | VS Code extension not on marketplace | Medium | Developer must side-load |
| 7 | CLI has no --help flag | Medium | Developer cannot discover flags |
| 8 | Error messages partially implemented | Medium | Some errors lack suggestions |
| 9 | Language spec version outdated | Medium | Confusion about current features |
| 10 | CLI reference incomplete | Medium | Missing 8+ commands |

### 4.3 Minor Gaps

| # | Gap | Severity | Impact |
|:-:|-----|:--------:|--------|
| 11 | Examples have stale comments | Low | Misleading about capabilities |
| 12 | No error message examples in docs | Low | Beginner cannot interpret errors |
| 13 | No difficulty ordering for examples | Low | Developer不知道 which to start with |

---

## 5. Mini Task Manager Specification

### 5.1 Features

**CRUD Operations:**
- `task_create(title, description, priority, assignee)`
- `task_find_by_id(task_id)`
- `task_update(task_id, field, value)`
- `task_delete(task_id)`
- `task_list_all()`

**Search:**
- `task_search(query)` — search title and description
- `task_filter_by_status(status)` — filter by status
- `task_filter_by_priority(priority)` — filter by priority

**Persistence:**
- `task_save_all()` — save to JSON file
- `task_load_all()` — load from JSON file

**Reports:**
- `task_report_by_status()` — count by status
- `task_report_by_priority()` — count by priority
- `task_report_overdue()` — find overdue tasks

**Permissions:**
- `auth_check_role(user_role, required_role)` — role hierarchy
- `auth_has_permission(user_role, permission)` — permission check

**Audit Log:**
- `audit_log_add(action, entity, details)` — log action
- `audit_log_list_by_entity(entity_id)` — list by entity
- `audit_log_list_recent(count)` — list recent entries

### 5.2 Data Model

```json
{
  "id": "task_001",
  "title": "Implement feature X",
  "description": "Detailed description...",
  "status": "open",
  "priority": "high",
  "assignee": "user_001",
  "created_at": "2026-07-14T10:00:00Z",
  "updated_at": "2026-07-14T10:00:00Z",
  "due_date": "2026-07-21T10:00:00Z"
}
```

### 5.3 File Structure

```
mini_task_manager/
├── main.ail          — Entry point, CLI routing
├── task.ail          — CRUD operations
├── search.ail        — Search and filter
├── storage.ail       — JSON persistence
├── report.ail        — Report generation
├── auth.ail          — Permission checks
├── audit_log.ail     — Audit logging
├── helpers.ail       — Shared utilities
└── tests/
    └── test_main.ail — Integration tests
```

### 5.4 Expected LOC

| File | Estimated LOC |
|------|:------------:|
| main.ail | 80 |
| task.ail | 120 |
| search.ail | 60 |
| storage.ail | 80 |
| report.ail | 60 |
| auth.ail | 40 |
| audit_log.ail | 50 |
| helpers.ail | 30 |
| tests/test_main.ail | 80 |
| **Total** | **~600** |

---

## 6. Recommendations

### 6.1 Before Recruiting External Developer

| Priority | Task | Owner | Status |
|:--------:|------|-------|:------:|
| P0 | Fix all 8 broken README doc links | Maintainer | ⏳ |
| P0 | Update STDLIB_REFERENCE with 21+ missing functions | Maintainer | ⏳ |
| P0 | Fix QUICKSTART Python version (3.9 → 3.11) | Maintainer | ⏳ |
| P1 | Add README to examples/ directory | Maintainer | ⏳ |
| P1 | Publish VS Code extension to marketplace | Maintainer | ⏳ |
| P2 | Update LANGUAGE_SPEC version (0.1.2 → 0.10.0) | Maintainer | ⏳ |
| P2 | Complete CLI reference (add 8+ commands) | Maintainer | ⏳ |

### 6.2 During Test

| Rule | Detail |
|------|--------|
| No intervention | Maintainer does not help, hint, or suggest |
| No source reading | Developer cannot read compiler/runtime source |
| No hidden knowledge | Developer only has documentation + examples |
| Screen recording | Full session recorded for analysis |
| Think-aloud | Developer narrates thought process |

### 6.3 After Test

| Deliverable | Purpose |
|-------------|---------|
| `docs/research/M67_EXTERNAL_ADOPTION.md` | Full test results and analysis |
| `docs/benchmarks/M67_ONBOARDING_RESULTS.md` | Metrics and comparison |
| `docs/releases/M67_ADOPTION_REPORT.md` | Executive summary and recommendations |

---

## 7. Answer to Final Question

> Can AILang succeed without its creators being present?

**Currently: No.**

The documentation audit reveals critical gaps that would block an external developer:

1. **Broken documentation links** — Every reference in README 404s
2. **Outdated stdlib reference** — Missing 21+ functions; claims existing functions are "missing"
3. **Undocumented examples** — 70+ files with no README, no index, no difficulty labels
4. **Wrong Python version** — QUICKSTART says 3.9+, compiler requires 3.11+
5. **No PyPI publication** — Developer cannot install without cloning

**These gaps are fixable.** Before recruiting an external developer, the maintainer must:

1. Fix all broken documentation links
2. Update STDLIB_REFERENCE with all 21+ missing functions
3. Fix QUICKSTART Python version
4. Add documentation to examples/
5. Publish to PyPI (or update QUICKSTART to reflect installation method)

**After fixing these gaps:** AILang has a chance to succeed without its creators. The language is deterministic, the compiler produces helpful error messages, and the VS Code extension provides IDE support. But the documentation must be complete and accurate first.

**The honest answer:** AILang cannot succeed without its creators **until the documentation is fixed**. The test protocol is valid, but the documentation gaps must be addressed first.

---

## 8. Next Steps

| Step | Action | Owner | Timeline |
|:----:|--------|-------|:--------:|
| 1 | Fix broken README doc links | Maintainer | Immediate |
| 2 | Update STDLIB_REFERENCE | Maintainer | This week |
| 3 | Fix QUICKSTART Python version | Maintainer | This week |
| 4 | Add examples README | Maintainer | This week |
| 5 | Publish to PyPI | Maintainer | Next week |
| 6 | Recruit external developer | Project lead | After step 5 |
| 7 | Execute M67 protocol | External developer | After step 6 |
| 8 | Analyze results | Maintainer | After step 7 |

---

## 9. References

| Document | Purpose |
|----------|---------|
| ADR-00X | Bounded Deterministic Iteration |
| M65A Recursion Audit | Evidence base for recursion friction |
| M66 Validation Report | For-in promotion decision |
| M67 Protocol | This document |
