# M69 — External Developer Validation

**Date:** 2026-07-14
**Status:** Protocol Defined
**Prerequisite:** M68.6 complete (PyPI publication)

---

## Objective

Validate that AILang's core thesis holds in practice:

> **Deterministic tooling can reduce developer correction cycles.**

The test is not whether AILang works. The test is whether a developer with zero prior knowledge can become productive without maintainer intervention.

---

## Validation Protocol

### Participants

| Type | Profile | Value |
|------|---------|-------|
| Python developer | Familiar with scripting, dynamic typing | Baseline comparison |
| Java/C# developer | Strong typing, compiled languages | Type system familiarity |
| Junior developer | Limited experience | Onboarding clarity |
| AI-assisted developer | Uses Copilot/ChatGPT | AI-first workflow |

### Tasks

| # | Task | Success Criteria | Measurement |
|---|------|------------------|-------------|
| 1 | Install AILang | `pip install ailang-lang` succeeds | Time, errors |
| 2 | Create project | `ail new hello` succeeds | Time, output clarity |
| 3 | Run hello world | `ail run main.ail` produces output | Time, output correctness |
| 4 | Read documentation | Navigate to relevant guide | Documentation lookups |
| 5 | Modify code | Edit main.ail, re-run | Time, errors |
| 6 | Fix compiler error | Introduce error, interpret diagnostic | Time, clarity rating |
| 7 | Use standard library | Import and use a module | Time, errors |
| 8 | Run tests | `ail test` succeeds | Time, output clarity |
| 9 | Build project | `ail build` succeeds | Time, output |
| 10 | Create new function | Write and call a custom function | Time, errors |

### Metrics

| Metric | Target |
|--------|--------|
| Participants | 4 |
| Critical interventions | 0 |
| Tooling failures | 0 |
| Compiler crashes | 0 |
| Documentation blockers | 0 |
| Median time to first successful build | < 30 minutes |
| Successful task completion | ≥ 90% |
| Total onboarding time | < 60 minutes |

### Intervention Classification

**Critical Intervention (Target = 0)**

Requires maintainer assistance to continue:

- Installation impossible
- Documentation missing required step
- Compiler bug
- Tooling failure

These are **failures**.

**Clarification Request (Valuable Signal)**

Developer asks a question but can continue independently:

- "Why does AILang require bottom-up ordering?"
- "Why no break/continue?"
- "Why immutable iterators?"

These are **research signals**, not failures.

### Hard Requirement

```
Critical interventions = 0
```

If critical intervention occurs, failure is classified as:

- **Documentation defect** — Information missing or unclear
- **Tooling defect** — Command failed or produced unclear output
- **Diagnostics defect** — Error message didn't help

Never classified as: **User error**

---

## Participant Onboarding Script

### Step 1: Installation

```
Welcome to AILang!

To install, run:
    pip install ailang-lang

To verify:
    ail --version

To create a project:
    ail new hello
    cd hello
    ail run main.ail
```

### Step 2: Documentation Access

```
Documentation:
    docs/reference/GETTING_STARTED.md — Step-by-step introduction
    docs/reference/LANGUAGE_TOUR.md — Complete language feature tour
    docs/reference/STDLIB_REFERENCE.md — All modules documented
    docs/QUICKSTART.md — 5-minute setup guide
```

### Step 3: Exercise

```
Build a simple calculator that:
1. Takes two numbers as variables
2. Adds them
3. Prints the result

Then extend it to:
4. Subtract, multiply, divide
5. Handle edge cases (division by zero)
```

---

## Success Scenarios

### Scenario A: Full Success

```
Participant completes all tasks in < 30 minutes
Maintainer intervention = 0
All metrics within targets
```

**Conclusion:** AILang's thesis validated. Proceed to M70 (Public Beta).

### Scenario B: Minor Issues

```
Participant completes most tasks
1-2 maintainer interventions needed
Issues are documentation or tooling, not language
```

**Conclusion:** Fix identified issues, re-test with next participant.

### Scenario C: Major Issues

```
Participant cannot complete core tasks
Multiple interventions required
Language design itself is the blocker
```

**Conclusion:** Pause M69, address fundamental issues, restart.

---

## Documentation Defect Tracking

If a participant gets stuck, log:

```yaml
defect_id: D001
participant: python_dev_01
task: 6 (fix compiler error)
issue: Diagnostic message unclear
metric: documentation_lookup
resolution: Add example to LANGUAGE_SPEC.md
severity: medium
```

---

## Post-M69 Actions

### If M69 Succeeds

1. Document results in `docs/benchmarks/M69_RESULTS.md`
2. Proceed to M70 (Public Beta)
3. Begin marketing/outreach
4. Set up community channels (Discord/GitHub Discussions)

### If M69 Fails

1. Categorize failures (documentation/tooling/language)
2. Create fix backlog
3. Address high-severity issues
4. Re-run M69 with new participants

---

## Strategic Importance

M69 is the final credibility test.

If M69 succeeds, AILang crosses:

```
Research Project
    ↓
Engineering Platform
    ↓
Ecosystem Candidate
```

This transition requires evidence that:

1. Documentation is sufficient
2. Diagnostics are helpful
3. Tooling is reliable
4. Onboarding is smooth
5. The language is learnable

Only real developers can provide this evidence.

---

## Timeline

| Phase | Duration | Activities |
|-------|----------|------------|
| M68.6 completion | 1-2 days | PyPI publication |
| M69 preparation | 1 day | Recruit participants, prepare materials |
| M69 execution | 3-5 days | Run validation sessions |
| M69 analysis | 1-2 days | Analyze results, create report |
| Total | 6-10 days | |

---

## Success = Evidence

The output of M69 is not a passing grade. The output is evidence:

- Which tasks are easy
- Which tasks are hard
- What documentation is missing
- What diagnostics are unclear
- What tooling is unreliable

This evidence drives M70 and beyond.
