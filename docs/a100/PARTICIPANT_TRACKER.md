# A100 Participant Tracker

**Coordinator use only.** Tracks recruitment and run status. Stores participant
IDs only — real names are never published. Every field below is a template;
fill with real data as it arrives. Do not backfill or fabricate rows.

---

## 1. Candidate pool

| Candidate ref | Independent (not contributor) | AI-assisted Python experience | AI-trusting | Committed to both phases | Contacted | Interested | Assigned ID |
|---------------|-------------------------------|-------------------------------|-------------|--------------------------|-----------|------------|-------------|
| C01 |  |  |  |  |  |  |  |

> Eligibility is all five conditions; any "no" → ineligible, note reason.

## 2. Assigned runs

| Participant ID | Build order (Python-first / AILang-first) | Randomized by | Date assigned |
|----------------|-------------------------------------------|---------------|---------------|
|  |  |  |  |

## 3. Run status

| Participant ID | Env verified (ail --version = v1.1.17) | Greenfield completed | Maintenance completed (M1–M6) | Form received | Consent to publish anonymized |
|----------------|----------------------------------------|----------------------|-------------------------------|---------------|-------------------------------|
|  |  |  |  |  |  |

## 4. Evidence log

| Participant ID | Date | First-impression bug (verbatim) | Severity (blocking/minor/cosmetic) | Feature request (verbatim) | Context |
|----------------|------|---------------------------------|-------------------------------------|----------------------------|---------|
|  |  |  |  |  |  |

> Severity "blocking" = prevented reaching first working version in the AILang
> run. Classify exactly; these feed the "0 release-blocking defects" criterion.

## 5. Raw forms storage

Completed data forms live in `docs/a100/results/P<ID>_FORM.md` (private,
not committed). Mark receipt in §3.

## 6. Cohort tally (fill only from real rows above)

| Metric | Target | Current |
|--------|--------|---------|
| Recruited (N) | >= 5 |  |
| Greenfield complete | 5/5 |  |
| Maintenance complete | >= 3/5 |  |
| Choose AILang next project | >= 3/5 |  |
| Release-blocking defects (v1.1.17) | 0 |  |

> Never adjust targets. Report the tally as-is when data exists.
