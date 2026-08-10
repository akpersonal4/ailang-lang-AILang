# A100 Participant Brief

**Milestone:** A100 — Community Validation (Active)
**Protocol authority:** `docs/roadmap/A100_COMMUNITY_VALIDATION.md` (canonical — this kit operationalizes it; in any conflict the protocol wins)
**Study package under test:** AILang v1.1.17 (published to PyPI + GitHub 2026-08-07)

---

## 1. Purpose of the Study

This is a two-phase head-to-head study: each participant builds one application
**twice** — once with Python + an AI assistant, once with AILang + an AI
assistant. The goal is to measure whether AILang's deterministic constraints
reduce the cost of building and maintaining business software for real users.

The study is an experiment. It is allowed to succeed or fail. The results are
recorded either way.

---

## 2. Who Can Participate (Eligibility — all must hold)

- **Independent:** not a contributor to the AILang repository or project.
- **AI-trusting:** already comfortable having an AI model author code.
- **AI-assisted Python experience:** hands-on experience with an AI-assisted
  Python workflow (required so the head-to-head comparison is meaningful).
- **Complete both phases:** commitment to finish greenfield build and, if
  reached, the maintenance phase.

No AILang experience is required — that is part of what is being measured.

---

## 3. What Participants Do

| Phase | Activity | Estimated time |
|-------|----------|----------------|
| Setup | Install both environments (instructions below) | ~20 min |
| Phase 1 — Greenfield | Build one application twice (Python, then AILang — or the reverse; order randomized) | ~1–2 h |
| Phase 2 — Maintenance | Apply a fixed sequence of change requests to the applications built in Phase 1 | ~1–2 h |
| Forms | Fill in the participant data-collection form after each phase | ~10 min each |

The order (Python-first vs AILang-first) is randomized per participant to
counterbalance familiarity effects. You will be told your order.

---

## 4. Environment Setup

### Python (AI-assisted)

- Python 3.11+ installed.
- Your usual AI coding tool (CLI, IDE extension, chat interface — your choice).

### AILang v1.1.17

- Install from PyPI (a source checkout is **not** used):

```bash
pip install ailang-lang==1.1.17
ail --version   # must print AILang v1.1.17
```

- If `ail --version` fails or shows a different version, stop and report it to
  the study coordinator **before** starting — that is a release-blocking defect
  finding, which is valuable data, not a failure of yours.
- Quick orientation (not part of the timed task): `ail doctor`, `ail check`,
  `ail run`, `ail testgen`. The study coordinator will provide the language
  guide (`docs/guides/AILANG_DEVELOPMENT_PLAYBOOK.md` content as a PDF) to read
  before the timed greenfield run. Reading it is allowed and encouraged.

---

## 5. The Two Choice Questions

At the end you will answer **both** of these — they are different data points:

1. Which was easier?
2. Which would you choose for your next project of the same kind?

You may honestly answer "Python was easier" and still answer "I would choose
AILang because maintenance felt safer." That distinction is exactly the
information the study is for.

---

## 6. What Is Measured

- Time to first working version (each phase).
- AI correction iterations (number of times you asked the AI to fix/redo work).
- Compiler/runtime error count (AILang) vs Python runtime/traceback errors.
- Frustration rating (self-reported).
- Confidence rating (self-reported, maintenance phase).
- Reliability of maintenance/change-request execution.
- The two choice questions above.

During the timed runs, you are asked to keep a simple event log (see the
data-collection form) rather than narrate aloud, to keep measurement consistent.

---

## 7. Consent, Anonymity, and Data Use

- All results are published **anonymized** (participant IDs only, e.g. P01–P05).
- Raw forms are stored privately and are not published.
- You may withdraw at any time; your partial data is excluded from the report
  unless you consent otherwise.
- Feature requests and bugs you report are recorded as study findings and routed
  through the project's governance process. They are **not** implemented during
  the study just to satisfy you — recording them is the point.

---

## 8. Things the Study Coordinator Will NOT Do

- Change the protocol, task spec, or success thresholds mid-study.
- Implement features during the study in response to participant feedback.
- Simulate or substitute synthetic participants.

---

## 9. Contact

Study coordinator: (coordinator contact). Report environment or setup problems
here; report technical findings in the form itself.
