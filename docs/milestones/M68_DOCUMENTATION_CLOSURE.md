# M68 — Documentation Closure Sprint

**Date:** 2026-07-14
**Status:** PLANNED
**Depends on:** M67 (External Adoption Validation)
**Blocks:** M69 (Real External Developer Validation)

---

## 1. Objective

Fix all documentation gaps identified in M67 to reach 90%+ documentation
readiness for external developers.

**Current state:** 41% ready
**Target state:** 90%+ ready

---

## 2. Context

M67 revealed that AILang's bottleneck is **documentation debt**, not language
or compiler instability. This is the best possible finding — documentation
is easier to fix than a broken compiler.

```
Before M67:
  Question: Can others use AILang?
  Answer:   Unknown.

After M67:
  Question: Why can't others use AILang today?
  Answer:   Documentation debt.
```

---

## 3. Gap Registry

| # | Gap | Severity | Fix Effort | Owner |
|:-:|-----|:--------:|:----------:|-------|
| 1 | All 8 README doc links broken | Critical | 1-2 hours | Maintainer |
| 2 | STDLIB_REFERENCE missing 21+ functions | Critical | 3-4 hours | Maintainer |
| 3 | Examples have zero documentation | High | 2-3 hours | Maintainer |
| 4 | QUICKSTART wrong Python version | Medium | 10 min | Maintainer |
| 5 | LANGUAGE_SPEC version outdated | Medium | 30 min | Maintainer |
| 6 | CLI reference incomplete | Medium | 1 hour | Maintainer |

**Total estimated effort: 8-10 hours (1.5 days)**

---

## 4. Task Breakdown

### 4.1 Gap #1: Fix Broken README Links

**Current state:** README.md links to 8 files that don't exist at referenced paths.

**Files to update:** `README.md`

**Changes:**

| Current Link | Correct Link |
|-------------|-------------|
| `docs/INSTALLATION.md` | `docs/reference/GETTING_STARTED.md` |
| `docs/GETTING_STARTED.md` | `docs/reference/GETTING_STARTED.md` |
| `docs/LANGUAGE_TOUR.md` | `docs/reference/LANGUAGE_TOUR.md` |
| `docs/STDLIB_REFERENCE.md` | `docs/reference/STDLIB_REFERENCE.md` |
| `docs/COMPILER_ARCHITECTURE.md` | `docs/reference/COMPILER_ARCHITECTURE.md` |
| `docs/CONTRIBUTING.md` | `docs/governance/CONTRIBUTING.md` |
| `docs/TESTING.md` | `docs/reference/TESTING.md` |
| `docs/INDEX.md` | `docs/archive/misc/INDEX.md` |

**Also fix:**
- Version badge (v0.3.0 → v1.0.0)
- Standard library table links

**Effort:** 1-2 hours

### 4.2 Gap #2: Update STDLIB_REFERENCE

**Current state:** Missing 21+ functions. Claims existing functions are "missing."

**File to update:** `docs/reference/STDLIB_REFERENCE.md`

**Functions to add:**

**string module (6 functions):**
- `find(value, needle)`
- `find_from(value, needle, start_pos)`
- `split(value, delim)`
- `join(values, separator)`
- `from_int(value)`
- `from_bool(value)`

**list module (13 functions):**
- `sort(values)`
- `sort_by_key(values, key)`
- `copy(values)`
- `find(values, key, value)`
- `filter(values, key, value)`
- `filter_by_key(values, key, value)`
- `filter_by_contains(values, key, substring)`
- `collect_key(values, key)`
- `group_by_key(values, key)`
- `sum_by_key(values, key)`
- `take(values, n)`
- `skip(values, n)`
- `search_by_name(values, query)`
- `exists_by_key(values, key, value)`

**map module (3 functions):**
- `get_or_default(values, key, default)`
- `safe_get(values, key, default)`
- `values(values)`

**Also fix:**
- Remove "Known Missing Operations" section (they're not missing)
- Fix invalid AILang syntax in examples (no list literals)
- Add examples for each function

**Effort:** 3-4 hours

### 4.3 Gap #3: Document Examples

**Current state:** 70+ example files with zero documentation.

**Files to create:** `examples/README.md` + per-example READMEs

**Structure:**

```markdown
# AILang Examples

## Quick Start
- hello_world — Hello World program
- calculator — Basic calculator

## Intermediate
- fibonacci — Recursive Fibonacci
- banking — Banking system with persistence

## Advanced
- static_analyzer — Self-analyzing tool
- inventory_mgmt — Full inventory system

## Patterns
- recursive_filter — Filter pattern
- recursive_map — Map pattern
- recursive_reduce — Reduce pattern

## Running Examples
```bash
ail run examples/hello_world/main.ail
```

**Also fix:**
- Remove stale comments ("not yet in AILang")
- Add difficulty labels
- Add stdlib module requirements

**Effort:** 2-3 hours

### 4.4 Gap #4: Fix QUICKSTART Python Version

**Current state:** Says "Python 3.9+" but compiler requires 3.11+.

**File to update:** `docs/QUICKSTART.md`

**Change:** Line with "Python 3.9+" → "Python 3.11+"

**Effort:** 10 minutes

### 4.5 Gap #5: Update LANGUAGE_SPEC Version

**Current state:** Says "Version: 0.1.2" but implementation is at v1.0.0.

**File to update:** `docs/reference/LANGUAGE_SPEC.md`

**Changes:**
- Update version header to v1.0.0
- Add `for` statement syntax (experimental)
- Update CLI reference (add 8+ commands)
- Add new error codes (PAR003, SEM003)

**Effort:** 30 minutes

### 4.6 Gap #6: Complete CLI Reference

**Current state:** Missing 8+ commands.

**File to update:** `docs/reference/LANGUAGE_SPEC.md` (Section 16)

**Commands to add:**
- `ail new` — Create new project
- `ail test` — Run tests
- `ail order` — Check dependency ordering
- `ail rename` — Rename identifiers
- `ail watch` — Watch for changes
- `ail install` — Install packages
- `ail add` — Add package dependency
- `ail remove` — Remove package dependency
- `ail update` — Update packages
- `ail list` — List installed packages
- `ail publish` — Publish package

**Effort:** 1 hour

---

## 5. Execution Order

| Order | Task | Depends On | Effort |
|:-----:|------|:----------:|:------:|
| 1 | Fix QUICKSTART Python version | None | 10 min |
| 2 | Fix broken README links | None | 1-2 hrs |
| 3 | Update STDLIB_REFERENCE | None | 3-4 hrs |
| 4 | Update LANGUAGE_SPEC version | None | 30 min |
| 5 | Complete CLI reference | #4 | 1 hr |
| 6 | Document examples | None | 2-3 hrs |
| 7 | Validate from clean machine | #1-6 | 1 hr |

**Parallelizable:** Tasks 1-3 can be done simultaneously.
**Total wall time: ~1.5 days** (with parallelism)

---

## 6. Success Criteria

| Criterion | Threshold | Measurement |
|-----------|:---------:|-------------|
| Documentation readiness | >= 90% | Audit score |
| README links | 0 broken | Manual check |
| STDLIB functions documented | 100% | Count documented vs actual |
| Examples documented | 100% | README exists for each |
| QUICKSTART accuracy | 100% | Clean machine test |
| LANGUAGE_SPEC version | v1.0.0 | Manual check |

---

## 7. Validation Protocol

After all fixes, validate from a clean machine:

```bash
# 1. Clean environment
python -m venv test_env
source test_env/bin/activate

# 2. Follow README.md instructions exactly
# 3. Follow QUICKSTART.md instructions exactly
# 4. Follow GETTING_STARTED.md instructions exactly
# 5. Try to build Mini Task Manager from M67 spec
# 6. Record any failures or confusion
```

**Success:** All instructions work without modification.
**Failure:** Any step requires maintainer intervention.

---

## 8. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| STDLIB functions have undocumented behavior | Medium | Medium | Read source code for each function |
| Examples have stale behavior | Low | Low | Run each example to verify |
| CLEAN MACHINE test reveals new gaps | Medium | High | Fix gaps as discovered |

---

## 9. Relationship to M69

M68 is a **prerequisite** for M69 (Real External Developer Validation).

```
M67 (Protocol) → M68 (Fix Docs) → M69 (Real Test) → Platform Complete
```

After M68:
- Documentation readiness: 90%+
- External developer can follow instructions
- No maintainer intervention required

After M69 (if pass):
- External developer succeeds
- AILang survives without creators
- Platform transition complete

---

## 10. References

| Document | Purpose |
|----------|---------|
| M67 External Adoption | Gap analysis and protocol |
| M67 Onboarding Results | Measurement framework |
| M67 Adoption Report | Executive summary |
