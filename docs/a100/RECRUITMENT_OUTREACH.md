# A100 Recruitment Outreach Pack

**Purpose:** ready-to-use, non-coaching outreach messages for recruiting
independent participants for the A100 Community Validation study.
**Baseline participants must use:** AILang v1.1.17 from PyPI (`pip install ailang-lang==1.1.17`).
**Public kit:** `docs/a100/` (on GitHub `main`), referenced in README.

> Rule for every message: present the study neutrally. Do not promise AILang is
> better, do not coach participants to prefer it, do not offer incentives tied to
> a positive result. Struggles and negative results are the evidence we want.

---

## Eligibility (restate verbatim from the Participant Brief)

- Independent: not a contributor to the AILang repository or project.
- AI-trusting: comfortable having an AI model author code.
- Hands-on AI-assisted Python experience.
- Commitment to complete the greenfield build and, if reached, the maintenance phase.

---

## 1. Short community post (for forums / Discord / Slack / LinkedIn)

```
Subject: Help measure AI-assisted development — small head-to-head study

I'm running an open, honest comparison study: build one small business CLI
app twice — once with Python + your AI tool, once with AILang + AI — then
apply the same change requests to both. ~1–2 h per phase.

Why: real numbers on whether deterministic language constraints reduce the
cost of AI-assisted business software. Results are anonymized. Negative
findings are welcome and published as-is.

Eligibility: you use an AI tool to write code and have prior AI-assisted
Python experience. Not open to contributors of the AILang project.

Docs (no signup, fully public):
https://github.com/akpersonal4/ailang-lang-AILang/blob/main/docs/a100/PARTICIPANT_BRIEF.md

The study uses the published v1.1.17 from PyPI, not a source checkout.
DM me if you're interested — I'll randomize your build order and send the
data form.
```

## 2. Private message / email (after someone expresses interest)

```
Thanks for volunteering. Here's what happens next:

1. Read the participant brief (link above).
2. Confirm you meet eligibility (independent, AI-assisted Python experience,
   available for both phases).
3. I'll assign you a build order (Python-first or AILang-first, randomized)
   and a participant ID.
4. Install the baseline:  pip install ailang-lang==1.1.17   (verify:
   ail --version  prints AILang v1.1.17). Use PyPI only — no source checkout.
5. Complete the greenfield task, then the maintenance tasks, using the exact
   specs in the public kit. Log your observations in the data form as you go.
6. Return the completed data form. Your ID, not your name, is published.

Time: roughly 1–2 h per phase, plus short forms. You can stop any time; your
partial data is excluded unless you consent otherwise.
```

## 3. Confirmation message at start of a run (anti-coaching)

```
Before you start: there is no "expected" outcome. If AILang makes the task
harder, record that exactly as it happens — a hard constraint and a slow build
are valid, useful data. If Python is smoother, say so. The study compares
measurements, not marketing.

Remember to log: install/first-use experience, time to first working version,
AI correction iterations, error counts, frustration/confidence, and the two
final preference questions answered separately.
```

---

## Coordinator checklist before each run

- [ ] Participant ID assigned (P01, P02, ...), no real names published
- [ ] Eligibility confirmed against the brief
- [ ] Build order randomized and recorded
- [ ] Environment verified: `ail --version` = AILang v1.1.17, installed from PyPI
- [ ] Data form handed over (electronic or printed)
- [ ] Event logs encouraged; no live coaching during timed runs
- [ ] Choice questions answered only after both languages' M6

## What to collect per participant (map to the form)

| Data | Where it lands in the report |
|------|------------------------------|
| Install / first-use experience | §D first-impression observations |
| Time to first working version | §4.1 greenfield table |
| AI correction iterations | §4.1 |
| Error counts (compiler vs runtime) | §4.1 |
| Frustration / confidence ratings | §4.1 / §4.2 |
| Greenfield experience | §4.1 |
| Maintenance experience (M1–M6) | §4.2 |
| Which was easier to build? | §5 Q1 |
| Which would you choose next? | §5 Q2 (separate) |
| First-impression bugs | §4.3 |
| Feature requests | §4.4 (recorded, never implemented mid-study) |

---

## Channels to try (coordinator-facing suggestions)

- Developer Discord/Slack communities focused on AI-assisted coding
- Local or remote meetup groups (Python, dev tooling)
- Professional network / former colleagues who use AI coding tools
- (Optional) open issue in the AILang repo inviting participants — text from §1

No fabricated participants, results, or testimonials — ever.
