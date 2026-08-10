# A100 — Community Validation

**Type:** First non-engineering milestone
**Status:** Active — recruitment ready
**Depends on:** v1.1.17 shipped with all precondition fixes (✅ shipped 2026-08-07)
**Success defined before recruitment:** yes (see Success Criteria)

---

## Objective

**Evaluate whether AILang's design produces measurable advantages for
AI-assisted business software development under real usage conditions.**

This wording is deliberate. It does not assume success. The milestone is an
experiment that is allowed to succeed or fail, and its outcome is recorded
either way.

---

## Why Now

Up to and including v1.1.16, every milestone asked a question about the
artifact:

- Does the compiler pass its tests?
- Do the benchmarks stay green?
- Is the wheel verifiable and reproducible?

Those questions are now answered (1217 tests, 5/5 canonical apps, verified
release). The limiting factor has moved from engineering to users. A100 asks
the question none of the internal work can answer:

- Does the engineering actually help a real person?

This is the project's first milestone whose pass/fail is decided by people
outside the repository.

---

## Framing: The Four-Question Progression

1. Can someone install it?
2. Can someone build something?
3. Would they use it again?
4. Would they choose it instead of an alternative?

A100 measures all four. Question 4 is the real benchmark: preference, not just
capability.

---

## Preconditions (ship before recruiting)

First-impression bugs cost more users than a parser optimization ever will. A
stranger does not see the architecture; they see the command that crashed.
These must be fixed and released before recruitment starts:

| Issue | Why it blocks A100 | Status |
|-------|--------------------|--------|
| `ail testgen <file>` crashes with an uncaught `ValueError` on a wheel install | A recruited developer can hit a traceback in minute five | ✅ Fixed in v1.1.17 |
| `ail benchmark` and `ail static-analyzer` require a source checkout | Contradicts "installed from PyPI" onboarding | ✅ Fixed in v1.1.17 (bundled apps) |
| `ail doctor` reports health score 0/100 on a wheel install | Alarming first impression for exactly the user we want to keep | ✅ Fixed in v1.1.17 |
| `ail rename` reports the wrong directory in its error message | Cosmetic, but cheap to fix before it is seen by a stranger | ✅ Fixed in v1.1.17 |

All four shipped in v1.1.17 (2026-08-07), released to PyPI + GitHub, and
verified post-publication from a fresh `pip install ailang-lang==1.1.17` venv:
8/8 CLI checks green, `ail doctor` 98/100, benchmark 5/5 apps.

Target: a fresh `pip install ailang-lang` reaches a first successful program
in under 10 minutes with zero tracebacks.

---

## Recruitment

- **Target:** at least 5 independent developers.
- **Persona:** AI-trusting developers (people already comfortable having a
  model author code). They tolerate constraints and value determinism; they are
  the natural early adopters of an AI-first language.
- **Experience filter:** participants must have hands-on experience with an
  AI-assisted Python workflow, so the head-to-head comparison is meaningful.
- **Recruitment channels:** AI developer communities, the project's GitHub,
  and any public AI-assisted-development showcases. No one may be a project
  contributor.

---

## Protocol: Two-Phase Head-to-Head

Each participant builds one application twice: once with Python + AI and once
with AILang + AI. Order is randomized to counterbalance familiarity effects.

### Phase 1 — Greenfield (build)

Task: build a new application from a fixed specification (e.g., an expense
tracker with CSV import, categories, and a summary report).

Measured:

- Time to first working version
- AI correction iterations
- Number of compiler/runtime errors
- Frustration rating (participant-reported)

Question asked:

> Which was easier to build?

### Phase 2 — Maintenance (change)

Both groups receive the same change requests, applied one at a time:

- Add GST (tax rate applied to all transactions)
- Add discounts (per-line percentage)
- Add a new CSV column
- Add role-based permissions (admin / user)
- Change tax rules (rate becomes per-category)
- Add an approval workflow

Measured:

- Time to implement each change
- Bugs introduced (regressions found by tests or review)
- AI correction iterations
- Confidence rating (participant-reported)

Question asked:

> Which was easier to maintain?

### The two choice questions are kept separate

Ask, and record, both — they are different data points:

1. Which was easier?
2. Which would you choose for your next project of the same kind?

A participant may honestly answer "Python was easier" while also answering "I
would choose AILang because maintenance felt safer." That distinction is
exactly the information A100 is for. Phase 2 is the central test of the
language's hypothesis; Phase 1 alone measures familiarity, not value.

---

## Success Criteria (fixed before recruitment)

| Metric | Success |
|--------|:-------:|
| Participants recruited | >= 5 |
| Useful application completed | >= 5 |
| Maintenance phase completed | >= 3 |
| Would choose AILang for the next project | >= 3 |
| Release-blocking bugs found during the study | 0 |

These are committed to before recruiting begins. They may not be redefined
afterward. "Release-blocking" follows the definition in `RELEASE_CHECKLIST.md`.

---

## Governance Principle

> **Community feedback identifies problems. Governance determines solutions.**

User reports from A100 drive the backlog. They do not override the six
governance questions in `AGENTS.md` §8. In particular, early feedback will
likely include requests that increase expressiveness (loops by default, nested
functions). Such requests are routed through the standard proposal process:
mission alignment, pain-point evidence, determinism impact. Adoption pressure
must not bypass engineering discipline.

---

## Deliverables

- `A100_VALIDATION_REPORT.md` — anonymized results: per-participant metrics for
  both phases, the two choice-question answers, first-impression bugs
  encountered, and a pass/fail verdict against the fixed criteria.
- Bug and feature findings routed into the issue tracker with severity tags.
- Feature requests routed through the governance proposal process.
- Lessons applied to the development playbook if they generalize.

## Execution Kit (`docs/a100/`)

Prepared materials that operationalize this protocol. In any conflict, this
protocol wins.

| File | Purpose |
|------|---------|
| `PARTICIPANT_BRIEF.md` | Eligibility, consent, environment setup (v1.1.17 from PyPI), timeline, what is measured |
| `GREENFIELD_TASK.md` | Exact Phase 1 spec — expense tracker (identical for both languages) |
| `MAINTENANCE_TASKS.md` | Exact Phase 2 spec — change requests M1–M6 (identical for both languages) |
| `DATA_COLLECTION_FORM.md` | Participant form capturing every protocol metric + event logs + first-impression bugs |
| `VALIDATION_REPORT_TEMPLATE.md` | Coordinator template for the final anonymized report + fixed-criteria verdict |

---

## Definition of Done

- All preconditions shipped in a released version.
- >= 5 participants recruited and run through both phases.
- Report published with a clear verdict against the fixed criteria.
- Every first-impression bug encountered is triaged (fixed or explicitly
  waived with a reason).
- No release-blocking bug left open from the study.

---

## Non-Goals

- No new language features as part of this milestone.
- No compiler work except the precondition fixes above and fixes for bugs the
  study surfaces.
- No target number of users beyond the fixed criteria.
- No marketing claims derived from the result; the report states what was
  measured, including negative findings.
